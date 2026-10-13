"""Freeze and collect local backend comparisons; never launch a hosted model."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path, PureWindowsPath
import re
import signal
import statistics
import subprocess
import sys
import threading
import time


CONDITIONS = {"aio", "compound-engineering", "superpowers"}
GATES = {"correctness", "security", "recovery"}
CAPTURE_LIMIT = 1024 * 1024
SCOPE = "Local evaluator observations only; does not launch/attest model generation or prove evaluator adequacy or production readiness."


class BenchmarkError(ValueError):
    pass


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise BenchmarkError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def read_json(path):
    with Path(path).open(encoding="utf-8-sig") as stream:
        return json.load(stream, object_pairs_hook=unique_object)


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def canonical_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def string(value, label):
    if not isinstance(value, str) or not value.strip():
        raise BenchmarkError(f"{label} must be a nonempty string")


def identifier(value, label):
    string(value, label)
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", value):
        raise BenchmarkError(f"{label} must be a simple stable identifier")


def exact(value, fields, label, optional=()):
    if (not isinstance(value, dict) or not set(fields).issubset(value)
            or set(value) - set(fields) - set(optional)):
        raise BenchmarkError(f"{label} must contain exactly: {', '.join(fields)}")


def strings(value, label):
    if not isinstance(value, list) or not value:
        raise BenchmarkError(f"{label} must be a nonempty array")
    for item in value:
        string(item, label)


def contained(root, relative):
    string(relative, "file path")
    normalized = relative.replace("\\", "/")
    windows = PureWindowsPath(relative)
    if (windows.drive or windows.root or normalized.startswith("/")
            or ".." in normalized.split("/") or ":" in normalized or "\0" in normalized):
        raise BenchmarkError("file path must be workspace-relative without traversal")
    path = (root / normalized).resolve(strict=True)
    if not path.is_relative_to(root) or not path.is_file():
        raise BenchmarkError("file path must resolve to a contained existing file")
    return path


def validate_definition(data):
    exact(data, ("schema_version", "status", "title", "task", "evaluator", "conditions", "trials", "settings", "gates", "metrics", "assertions"), "definition", ("score_format", "gate_categories"))
    if type(data["schema_version"]) is not int or data["schema_version"] != 1 or data["status"] != "ready":
        raise BenchmarkError("definition must have schema_version 1 and status ready")
    for field in ("title", "task", "evaluator"):
        string(data[field], field)
    strings(data["conditions"], "conditions")
    if (not 2 <= len(data["conditions"]) <= len(CONDITIONS)
            or len(set(data["conditions"])) != len(data["conditions"])
            or not set(data["conditions"]).issubset(CONDITIONS)):
        raise BenchmarkError("conditions must contain 2 or 3 unique supported IDs: aio, compound-engineering, superpowers")
    strings(data["gates"], "gates")
    if len(data["gates"]) != len(GATES) or set(data["gates"]) != GATES:
        raise BenchmarkError("gates must contain correctness, security and recovery exactly once")
    if not isinstance(data["settings"], dict) or not data["settings"]:
        raise BenchmarkError("settings must be a nonempty object recorded before generation")
    strings(data["assertions"], "assertions")
    if not isinstance(data["trials"], list) or not data["trials"]:
        raise BenchmarkError("trials must be nonempty")
    seen = set()
    for item in data["trials"]:
        exact(item, ("id", "seed"), "trial")
        identifier(item["id"], "trial.id")
        if item["id"] in seen or type(item["seed"]) is not int:
            raise BenchmarkError("trials require unique IDs and integer seeds")
        seen.add(item["id"])
    if not isinstance(data["metrics"], list) or not data["metrics"]:
        raise BenchmarkError("metrics must be nonempty")
    seen = set()
    for item in data["metrics"]:
        exact(item, ("id", "direction"), "metric")
        identifier(item["id"], "metric.id")
        if item["id"] in seen or item["direction"] not in ("lower", "higher"):
            raise BenchmarkError("metrics require unique IDs and lower/higher direction")
        seen.add(item["id"])
    score_format = data.get("score_format", "gates")
    if score_format not in ("gates", "test-report"):
        raise BenchmarkError("score_format must be gates or test-report")
    if score_format == "test-report":
        exact(data.get("gate_categories"), data["gates"], "gate_categories")
        for categories in data["gate_categories"].values():
            strings(categories, "gate_categories")
        if seen - {"total_tests", "passed_tests", "failed_tests", "pass_rate"}:
            raise BenchmarkError("test-report metrics are total_tests, passed_tests, failed_tests or pass_rate")
    elif "gate_categories" in data:
        raise BenchmarkError("gate_categories applies only to test-report format")
    canonical_digest(data)  # Reject non-finite JSON metadata too.


def write_new(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")


def freeze(definition, root, output):
    data = read_json(definition)
    validate_definition(data)
    frozen = {"schema_version": 1, "definition": data,
              "definition_sha256": canonical_digest(data),
              "task_sha256": digest(contained(root, data["task"])),
              "evaluator_sha256": digest(contained(root, data["evaluator"])),
              "frozen_at": datetime.now(timezone.utc).isoformat()}
    write_new(output, frozen)
    return frozen


def load_frozen(path, root):
    frozen = read_json(path)
    exact(frozen, ("schema_version", "definition", "definition_sha256", "task_sha256", "evaluator_sha256", "frozen_at"), "frozen protocol")
    if type(frozen["schema_version"]) is not int or frozen["schema_version"] != 1:
        raise BenchmarkError("frozen schema_version must be integer 1")
    validate_definition(frozen["definition"])
    if canonical_digest(frozen["definition"]) != frozen["definition_sha256"]:
        raise BenchmarkError("frozen definition digest mismatch")
    for field in ("task", "evaluator"):
        if digest(contained(root, frozen["definition"][field])) != frozen[field + "_sha256"]:
            raise BenchmarkError(f"frozen {field} content changed")
    return frozen


def _capture(stream, target):
    chunks = []
    count = 0
    stored = 0
    try:
        for block in iter(lambda: stream.read(65536), b""):
            count += len(block)
            available = max(0, CAPTURE_LIMIT - stored)
            if available:
                chunks.append(block[:available])
                stored += min(available, len(block))
    finally:
        stream.close()
        target.update(data=b"".join(chunks), bytes=count)


def execute(command, root, environment, timeout):
    options = {"cwd": root, "env": environment, "stdout": subprocess.PIPE, "stderr": subprocess.PIPE, "shell": False}
    if os.name == "nt":
        options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        options["start_new_session"] = True
    start = time.perf_counter()
    process = subprocess.Popen(command, **options)
    stdout, stderr = {}, {}
    readers = [threading.Thread(target=_capture, args=(process.stdout, stdout), daemon=True),
               threading.Thread(target=_capture, args=(process.stderr, stderr), daemon=True)]
    for reader in readers:
        reader.start()
    timed_out = False
    cleanup_warnings = []
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        if os.name == "nt":
            try:
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10, check=True)
            except (OSError, subprocess.SubprocessError) as error:
                cleanup_warnings.append(f"Process-tree cleanup failed; direct child cleanup still attempted: {error}")
        else:
            os.killpg(process.pid, signal.SIGKILL)
        if process.poll() is None:
            process.kill()
        process.wait(timeout=10)
    for reader in readers:
        reader.join(timeout=10)
    if any(reader.is_alive() for reader in readers):
        raise BenchmarkError("evaluator left inherited output streams open; clean up its descendant processes")
    return {"command": command, "exit_code": process.returncode,
            "timed_out": timed_out, "elapsed_seconds": time.perf_counter() - start,
            "cleanup_warnings": cleanup_warnings,
            "stdout": stdout["data"].decode("utf-8", errors="replace"),
            "stderr": stderr["data"].decode("utf-8", errors="replace"),
            "stdout_bytes": stdout["bytes"], "stderr_bytes": stderr["bytes"],
            "stdout_sha256": hashlib.sha256(stdout["data"]).hexdigest(),
            "stderr_sha256": hashlib.sha256(stderr["data"]).hexdigest()}


def finite_number(value):
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def validate_evaluation(data, definition):
    exact(data, ("gates", "metrics", "notes"), "evaluator result")
    exact(data["gates"], definition["gates"], "evaluator gates")
    if any(type(value) is not bool for value in data["gates"].values()):
        raise BenchmarkError("evaluator gates must be booleans")
    metrics = [item["id"] for item in definition["metrics"]]
    exact(data["metrics"], metrics, "evaluator metrics")
    if any(not finite_number(value) for value in data["metrics"].values()):
        raise BenchmarkError("evaluator metrics must be finite numbers, never booleans")
    if not isinstance(data["notes"], list):
        raise BenchmarkError("evaluator notes must be an array")
    for note in data["notes"]:
        string(note, "evaluator note")


def normalize_evaluation(raw, definition):
    if definition.get("score_format", "gates") == "gates":
        validate_evaluation(raw, definition)
        return raw
    exact(raw, ("total", "passed", "failed", "errors", "categories", "tests"), "test report")
    if (any(type(raw[key]) is not int or raw[key] < 0 for key in ("total", "passed", "failed"))
            or not isinstance(raw["tests"], list) or not raw["tests"]
            or not isinstance(raw["errors"], list) or not isinstance(raw["categories"], dict)):
        raise BenchmarkError("test report requires nonnegative integer counts, nonempty tests, categories object and errors array")
    categories = {category for values in definition["gate_categories"].values() for category in values}
    ids = set()
    passed = 0
    for test in raw["tests"]:
        if not isinstance(test, dict) or not {"id", "status", "category"}.issubset(test):
            raise BenchmarkError("each scored test requires id/status/category")
        identifier(test["id"], "test.id")
        string(test["category"], "test.category")
        if test["id"] in ids or test["status"] not in ("passed", "failed", "error") or test["category"] not in categories:
            raise BenchmarkError("scored tests require unique IDs, known status and frozen gate category")
        ids.add(test["id"])
        passed += test["status"] == "passed"
    if (raw["total"], raw["passed"], raw["failed"]) != (len(ids), passed, len(ids) - passed):
        raise BenchmarkError("test report totals disagree with individual outcomes")
    gates = {}
    for gate, names in definition["gate_categories"].items():
        selected = [test for test in raw["tests"] if test["category"] in names]
        gates[gate] = bool(selected) and not raw["errors"] and all(test["status"] == "passed" for test in selected)
    available = {"total_tests": len(ids), "passed_tests": passed,
                 "failed_tests": len(ids) - passed, "pass_rate": passed / len(ids)}
    result = {"gates": gates, "metrics": {item["id"]: available[item["id"]] for item in definition["metrics"]}, "notes": []}
    validate_evaluation(result, definition)
    return result


def collect(frozen_path, root, condition, trial, artifact, output, command, timeout=60):
    frozen = load_frozen(frozen_path, root)
    definition = frozen["definition"]
    if condition not in definition["conditions"]:
        raise BenchmarkError("condition was not declared before generation")
    trials = {item["id"]: item["seed"] for item in definition["trials"]}
    if trial not in trials:
        raise BenchmarkError("trial was not declared before generation")
    if not command or not 0 < timeout <= 3600 or not math.isfinite(timeout):
        raise BenchmarkError("caller must supply explicit evaluator argv and timeout in (0, 3600]")
    evaluator = contained(root, definition["evaluator"])
    if not any((root / item).resolve() == evaluator for item in command):
        raise BenchmarkError("explicit argv must include the frozen evaluator file")
    artifact_path = contained(root, artifact)
    artifact_hash = digest(artifact_path)
    if Path(output).exists():
        raise BenchmarkError("collection output already exists; preserve the original run")
    environment = os.environ.copy()
    environment.update(AIO_BENCHMARK_ARTIFACT=str(artifact_path),
                       AIO_BENCHMARK_TASK=str(contained(root, definition["task"])),
                       AIO_BENCHMARK_CONDITION=condition,
                       AIO_BENCHMARK_TRIAL=trial, AIO_BENCHMARK_SEED=str(trials[trial]))
    record = {"schema_version": 1, "definition_sha256": frozen["definition_sha256"],
              "task_sha256": frozen["task_sha256"], "evaluator_sha256": frozen["evaluator_sha256"],
              "condition": condition, "trial": trial, "seed": trials[trial],
              "artifact": artifact, "artifact_sha256": artifact_hash,
              "execution": None, "result": None, "errors": [], "scope": SCOPE}
    try:
        execution = execute(command, root, environment, timeout)
        record["execution"] = execution
        if execution["timed_out"]:
            raise BenchmarkError("evaluator timed out")
        if execution["exit_code"] != 0:
            record["errors"].append(f"evaluator exited {execution['exit_code']}")
        if max(execution["stdout_bytes"], execution["stderr_bytes"]) > CAPTURE_LIMIT:
            raise BenchmarkError("evaluator output exceeded 1 MiB capture limit")
        raw = json.loads(execution["stdout"], object_pairs_hook=unique_object)
        result = normalize_evaluation(raw, definition)
        load_frozen(frozen_path, root)
        if digest(artifact_path) != artifact_hash:
            raise BenchmarkError("artifact changed during evaluator execution")
        record["result"] = result
    except (BenchmarkError, OSError, ValueError, subprocess.SubprocessError) as error:
        record["errors"].append(str(error))
    write_new(output, record)
    return record


def compare(frozen_path, root, result_paths, output):
    frozen = load_frozen(frozen_path, root)
    definition = frozen["definition"]
    trials = {item["id"]: item["seed"] for item in definition["trials"]}
    expected = {(condition, trial) for condition in definition["conditions"] for trial in trials}
    records = {}
    for path in result_paths:
        item = read_json(path)
        exact(item, ("schema_version", "definition_sha256", "task_sha256", "evaluator_sha256", "condition", "trial", "seed", "artifact", "artifact_sha256", "execution", "result", "errors", "scope"), "collection record")
        if type(item["schema_version"]) is not int or item["schema_version"] != 1 or type(item["seed"]) is not int:
            raise BenchmarkError("collection schema_version must be integer 1 and seed an integer")
        for key in ("definition_sha256", "task_sha256", "evaluator_sha256"):
            if item[key] != frozen[key]:
                raise BenchmarkError("collection records must share the frozen protocol and input hashes")
        key = (item["condition"], item["trial"])
        if key not in expected or key in records or item["seed"] != trials.get(item["trial"]):
            raise BenchmarkError("collection pairs must be declared, unique and use the frozen seed")
        if not isinstance(item["errors"], list):
            raise BenchmarkError("collection errors must be an array")
        for error in item["errors"]:
            string(error, "collection error")
        if not item["errors"]:
            if not isinstance(item["execution"], dict) or item["execution"].get("exit_code") != 0 or item["execution"].get("timed_out") is not False:
                raise BenchmarkError("successful collection requires a completed evaluator execution")
            validate_evaluation(item["result"], definition)
        records[key] = item
    if set(records) != expected:
        raise BenchmarkError("comparison requires every declared condition/trial, including failures")
    conditions = []
    for condition in definition["conditions"]:
        runs = [records[(condition, trial)] for trial in trials]
        eligible = all(not run["errors"] and all(run["result"]["gates"].values()) for run in runs)
        metrics = {}
        if eligible:
            for metric in definition["metrics"]:
                values = [run["result"]["metrics"][metric["id"]] for run in runs]
                metrics[metric["id"]] = {"direction": metric["direction"], "count": len(values),
                                        "mean": statistics.mean(values), "minimum": min(values),
                                        "maximum": max(values), "values": values}
        conditions.append({"condition": condition, "eligible_for_metrics": eligible,
                           "trials": runs, "metrics": metrics})
    report = {"schema_version": 1, "definition_sha256": frozen["definition_sha256"],
              "settings_declared": definition["settings"], "conditions": conditions, "scope": SCOPE}
    write_new(output, report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    children = parser.add_subparsers(dest="operation", required=True)
    for name in ("freeze", "collect", "compare"):
        child = children.add_parser(name)
        child.add_argument("protocol", type=Path)
        child.add_argument("--root", required=True, type=Path)
        child.add_argument("--output", required=True, type=Path)
        if name == "collect":
            child.add_argument("--condition", required=True)
            child.add_argument("--trial", required=True)
            child.add_argument("--artifact", required=True)
            child.add_argument("--timeout", type=float, default=60)
        if name == "compare":
            child.add_argument("--results", nargs="+", required=True, type=Path)
    supplied = list(sys.argv[1:] if argv is None else argv)
    command = []
    if "--" in supplied:
        split = supplied.index("--")
        supplied, command = supplied[:split], supplied[split + 1:]
    args = parser.parse_args(supplied)
    try:
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise BenchmarkError("root must be an existing directory")
        if args.operation == "freeze":
            result = freeze(args.protocol, root, args.output)
        elif args.operation == "collect":
            result = collect(args.protocol, root, args.condition, args.trial, args.artifact, args.output, command, args.timeout)
        else:
            result = compare(args.protocol, root, args.results, args.output)
        print(json.dumps({"output": str(args.output), "scope": SCOPE}))
        return 1 if args.operation == "collect" and (result["errors"] or not all(result["result"]["gates"].values())) else 0
    except (BenchmarkError, OSError, ValueError, TypeError, RecursionError) as error:
        print(f"Benchmark error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
