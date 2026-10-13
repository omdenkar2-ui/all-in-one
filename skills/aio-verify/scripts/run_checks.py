#!/usr/bin/env python3
"""Run explicitly configured checks; bounded evidence, never an inferred health score."""
from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import json
import math
import os
from pathlib import Path, PureWindowsPath
import re
import shutil
import subprocess
import sys
import time
import uuid

CONFIG_LIMIT = 65536
READ_SIZE = 65536
DRAIN_SECONDS = 1.0
CLEANUP_SECONDS = 2.0
LIMITS = {"timeout_seconds": (30, 0.1, 600),
          "run_timeout_seconds": (300, 0.1, 900),
          "max_log_bytes": (262144, 1, 4194304)}
CLEANUP_SCOPE = "direct child only; descendants may survive or keep pipes open"


def timestamp():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")


def relative_path(root, value):
    """Reject escapes and symlink/reparse escapes; this is not a filesystem sandbox."""
    if not isinstance(value, str) or not value or len(value) > 2048 or "\x00" in value:
        raise ValueError("path must be a nonempty workspace-relative string")
    win = PureWindowsPath(value)
    path = Path(value)
    if path.is_absolute() or win.drive or win.root or ".." in path.parts or ".." in win.parts:
        raise ValueError("path must stay inside the workspace: " + value)
    # Win32 strips trailing dots/spaces and supports colon stream aliases.
    # Reject them before the lexical .git guard, on every host for portability.
    if any(part.endswith((".", " ")) or ":" in part for part in (*path.parts, *win.parts)):
        raise ValueError("path cannot use trailing dot/space aliases or alternate streams: " + value)
    if any(part.lower() == ".git" for part in path.parts):
        raise ValueError(".git paths are not check evidence/configuration paths")
    target = root / path
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("symlink paths are not allowed: " + value)
        if current.exists():
            try:
                current.resolve(strict=True).relative_to(root)
            except ValueError as exc:
                raise ValueError("resolved path escapes the workspace: " + value) from exc
    target.resolve(strict=False).relative_to(root)
    return target


def number(value, name):
    _, minimum, maximum = LIMITS[name]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(name + " must be a finite number")
    if not minimum <= value <= maximum or (name == "max_log_bytes" and not isinstance(value, int)):
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def fields(value, allowed, context):
    if not isinstance(value, dict) or set(value) - allowed:
        raise ValueError(context + " must be an object containing only " + ", ".join(sorted(allowed)))


def load_config(root, config_path):
    path = relative_path(root, config_path)
    with path.open("rb") as handle:
        raw = handle.read(CONFIG_LIMIT + 1)
    if len(raw) > CONFIG_LIMIT:
        raise ValueError("configuration exceeds 65536 bytes")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate configuration field: " + key)
            result[key] = value
        return result
    config = json.loads(raw.decode("utf-8"), object_pairs_hook=unique)
    fields(config, {"schema_version", "limits", "checks"}, "configuration")
    if type(config.get("schema_version")) is not int or config["schema_version"] != 1:
        raise ValueError("schema_version must be 1")
    limits = config.get("limits", {})
    fields(limits, set(LIMITS), "limits")
    limits = {name: number(limits.get(name, LIMITS[name][0]), name) for name in LIMITS}
    checks = config.get("checks")
    if not isinstance(checks, list) or not 1 <= len(checks) <= 32:
        raise ValueError("checks must contain 1 to 32 explicitly configured checks")
    ids = set()
    prepared = []
    for check in checks:
        fields(check, {"id", "argv", "cwd", "requires", "timeout_seconds"}, "check")
        name = check.get("id")
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", name) or name in ids:
            raise ValueError("check ids must be unique ASCII letters/digits/underscore/hyphen, at most 64 characters")
        ids.add(name)
        argv = check.get("argv")
        if (not isinstance(argv, list) or not 1 <= len(argv) <= 128 or
            any(not isinstance(arg, str) or len(arg) > 8192 or "\x00" in arg for arg in argv) or
            not argv[0] or sum(len(arg) for arg in argv) > 16384):
            raise ValueError("argv must be 1 to 128 literal strings, at most 16384 characters total")
        cwd = check.get("cwd")
        relative_path(root, cwd)
        requires = check.get("requires", [])
        if not isinstance(requires, list) or len(requires) > 32:
            raise ValueError("requires must be a list of up to 32 workspace-relative paths")
        for item in requires:
            relative_path(root, item)
        timeout = number(check.get("timeout_seconds", limits["timeout_seconds"]), "timeout_seconds")
        prepared.append({"id": name, "argv": argv, "cwd": cwd,
                         "requires": requires, "timeout_seconds": timeout})
    return {"schema_version": 1, "limits": limits, "checks": prepared}, path


def private_directory(path):
    """Create exclusively; Windows inherits the existing workspace ACL."""
    path.mkdir(mode=0o700)


def exclusive_file(path):
    return os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb", buffering=0)


def write_bytes(handle, data):
    view = memoryview(data)
    while view:
        written = handle.write(view)
        if not written:
            raise OSError("evidence write made no progress")
        view = view[written:]


def write_json(path, value):
    with exclusive_file(path) as handle:
        write_bytes(handle, (json.dumps(value, ensure_ascii=True, indent=2) + "\n").encode("utf-8"))


def available_bytes(stream):
    if os.name != "nt":
        return READ_SIZE
    from ctypes import wintypes
    import msvcrt
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.PeekNamedPipe.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD,
                                   ctypes.c_void_p, ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
    kernel.PeekNamedPipe.restype = wintypes.BOOL
    available = wintypes.DWORD()
    if not kernel.PeekNamedPipe(msvcrt.get_osfhandle(stream.fileno()), None, 0, None, ctypes.byref(available), None):
        error = ctypes.get_last_error()
        if error in (109, 233):  # Broken/disconnected pipe: EOF.
            return -1
        raise ctypes.WinError(error)
    return min(available.value, READ_SIZE)


def executable(argv, cwd):
    command = argv[0]
    if os.path.dirname(command):
        path = Path(command)
        candidate = path if path.is_absolute() else cwd / path
        found = str(candidate.resolve()) if candidate.is_file() else None
    else:
        found = shutil.which(command)
    if found and Path(found).suffix.lower() in {".cmd", ".bat"}:
        raise ValueError("batch launchers may invoke a shell implicitly; configure an explicit executable instead")
    return str(Path(found).resolve()) if found else None


def terminate_owned(process):
    if process is not None and process.poll() is None:
        process.kill()
        process.wait(timeout=CLEANUP_SECONDS)


def run_check(root, output, check, index, limits, suite_deadline):
    base = f"{index:02d}"
    result = {"id": check["id"], "argv": check["argv"], "cwd": check["cwd"],
              "started_at": timestamp(), "completed_at": None, "duration_seconds": 0,
              "status": "capture_error", "exit_code": None, "capture_complete": False,
              "logs": {}, "reason": None}
    started = time.monotonic()
    process = None
    streams = {}
    logs = {}
    try:
        cwd = relative_path(root, check["cwd"])
        missing = [item for item in check["requires"] if not relative_path(root, item).exists()]
        if not cwd.is_dir() or missing:
            result.update(status="prerequisite_missing", reason="missing cwd or required paths: " + ", ".join(missing or [check["cwd"]]))
            return result
        found = executable(check["argv"], cwd)
        if found is None:
            result.update(status="missing_tool", reason="configured executable unavailable")
            return result
        remaining = suite_deadline - time.monotonic()
        if remaining <= 0:
            result.update(status="budget_exhausted", reason="run timeout budget exhausted; check did not execute")
            return result
        for name in ("stdout", "stderr"):
            path = output / (base + "." + name + ".log")
            logs[name] = exclusive_file(path)
            result["logs"][name] = {"path": str(path.relative_to(root)), "bytes_seen": 0,
                                     "bytes_retained": 0, "truncated": False, "eof": False}
        try:
            process = subprocess.Popen(check["argv"], executable=found, cwd=cwd, stdin=subprocess.DEVNULL,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, bufsize=0)
        except OSError as exc:
            result.update(status="launch_error", reason=str(exc))
            return result
        streams = {"stdout": process.stdout, "stderr": process.stderr}
        if os.name != "nt":
            for stream in streams.values():
                os.set_blocking(stream.fileno(), False)
        deadline = min(time.monotonic() + check["timeout_seconds"], suite_deadline)
        exited_at = None
        timed_out = False
        interrupted = False
        while True:
            try:
                active = False
                for name, stream in streams.items():
                    detail = result["logs"][name]
                    if detail["eof"]:
                        continue
                    count = available_bytes(stream)
                    if count == -1:
                        detail["eof"] = True
                        continue
                    if count == 0:
                        continue
                    try:
                        chunk = os.read(stream.fileno(), count)
                    except BlockingIOError:
                        continue
                    if not chunk:
                        detail["eof"] = True
                        continue
                    active = True
                    detail["bytes_seen"] += len(chunk)
                    room = limits["max_log_bytes"] - detail["bytes_retained"]
                    retained = chunk[:max(0, room)]
                    if retained:
                        write_bytes(logs[name], retained)
                        detail["bytes_retained"] += len(retained)
                    detail["truncated"] = detail["bytes_seen"] > detail["bytes_retained"]
                code = process.poll()
                now = time.monotonic()
                if code is None and now >= deadline:
                    timed_out = True
                    terminate_owned(process)
                    code = process.returncode
                if code is not None:
                    if exited_at is None:
                        exited_at = now
                    if all(detail["eof"] for detail in result["logs"].values()) or now - exited_at >= DRAIN_SECONDS:
                        break
                if not active:
                    time.sleep(0.01)
            except KeyboardInterrupt:
                interrupted = True
                terminate_owned(process)
                break
        result["exit_code"] = process.returncode
        result["capture_complete"] = all(detail["eof"] and not detail["truncated"] for detail in result["logs"].values())
        if interrupted:
            result.update(status="interrupted", reason="interrupted; direct child terminated")
        elif timed_out:
            result.update(status="timeout", reason="check or remaining run timeout exceeded")
        elif process.returncode != 0:
            result.update(status="failed", reason="checker returned nonzero")
        elif not result["capture_complete"]:
            result.update(status="incomplete_output", reason="log limit reached or pipes remained open after direct child exit")
        else:
            result.update(status="passed", reason=None)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        result.update(status="capture_error", reason=str(exc))
    finally:
        try:
            terminate_owned(process)
        except (OSError, subprocess.TimeoutExpired) as exc:
            result.update(status="cleanup_error", reason=str(exc))
        if process is not None:
            result["exit_code"] = process.poll()
        for handle in list(streams.values()) + list(logs.values()):
            try:
                handle.close()
            except OSError as exc:
                result.update(status="capture_error", capture_complete=False, reason=str(exc))
        result["completed_at"] = timestamp()
        result["duration_seconds"] = round(time.monotonic() - started, 3)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", help="workspace-relative JSON configuration")
    parser.add_argument("--root", required=True, help="explicit workspace root")
    parser.add_argument("--output-dir", help="new workspace-relative directory; parent must already exist")
    parser.add_argument("--validate", action="store_true", help="validate configuration only; launch nothing")
    args = parser.parse_args(argv)
    try:
        root = Path(args.root).resolve(strict=True)
        if not root.is_dir():
            raise ValueError("workspace root must be a directory")
        config, config_path = load_config(root, args.config)
        if args.validate:
            print(json.dumps({"status": "valid", "check_count": len(config["checks"]), "limits": config["limits"]}))
            return 0
        output = relative_path(root, args.output_dir or ("aio-checks-" + uuid.uuid4().hex))
        if not output.parent.is_dir():
            raise ValueError("output parent must already exist")
        private_directory(output)
        write_json(output / "config.json", config)
        started = timestamp()
        deadline = time.monotonic() + config["limits"]["run_timeout_seconds"]
        results = []
        for index, check in enumerate(config["checks"], 1):
            result = run_check(root, output, check, index, config["limits"], deadline)
            result["evidence_path"] = str((output / f"{index:02d}.result.json").relative_to(root))
            try:
                write_json(root / result["evidence_path"], result)
            except OSError as exc:
                result["evidence_path"] = None
                result["evidence_error"] = str(exc)
                if result["status"] == "passed":
                    result.update(status="capture_error", capture_complete=False, reason="result evidence could not be written")
            results.append(result)
            if result["status"] == "interrupted":
                break
        summary_path = output / "summary.json"
        passed = len(results) == len(config["checks"]) and all(item["status"] == "passed" for item in results)
        summary = {"schema_version": 1, "status": "passed" if passed else "not_passed",
                   "workspace": str(root), "config_path": str(config_path.relative_to(root)),
                   "started_at": started, "completed_at": timestamp(), "limits": config["limits"],
                   "configured_checks": len(config["checks"]), "cleanup_scope": CLEANUP_SCOPE,
                   "log_privacy": "workspace ACL inheritance" if os.name == "nt" else "owner-only POSIX modes",
                   "results": results}
        write_json(summary_path, summary)
        concise = {"status": summary["status"], "summary_path": str(summary_path.relative_to(root)),
                   "cleanup_scope": CLEANUP_SCOPE, "configured_checks": len(config["checks"]),
                   "results": [{key: item[key] for key in ("id", "status", "exit_code", "capture_complete", "duration_seconds", "evidence_path")} for item in results]}
        print(json.dumps(concise, ensure_ascii=True))
        return 0 if passed else (130 if any(item["status"] == "interrupted" for item in results) else 1)
    except (OSError, ValueError, UnicodeError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
