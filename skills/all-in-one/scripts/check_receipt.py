"""Check completion claims against caller-supplied files, without running commands.

This checker verifies receipt structure, current contract SHA256, and local file
availability. It cannot authenticate test output, establish production correctness,
or prove that a pull request or deployment occurred.
"""

import argparse
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import sys
from urllib.parse import urlsplit


SCOPE = (
    "Checks structure, contract SHA256, and local evidence availability only; "
    "does not authenticate commands or remote delivery, or prove backend correctness."
)


class _Validation:
    def __init__(self, root):
        self.root = root
        self.errors = []

    def error(self, message):
        self.errors.append(message)

    def obj(self, value, label, required, optional=()):
        if not isinstance(value, dict):
            self.error(f"{label} must be an object")
            return {}
        for key in required:
            if key not in value:
                self.error(f"{label}.{key} is required")
        for key in value:
            if key not in required and key not in optional:
                self.error(f"{label}: unknown field {key!r}")
        return value

    def seq(self, value, label, nonempty=False):
        if not isinstance(value, list):
            self.error(f"{label} must be an array")
            return []
        if nonempty and not value:
            self.error(f"{label} must not be empty")
        return value

    def string(self, value, label):
        if not isinstance(value, str) or not value.strip():
            self.error(f"{label} must be a nonempty string")
            return False
        return True

    def enum(self, value, label, options):
        if value not in options:
            self.error(f"{label} must be one of {', '.join(options)}")
            return False
        return True

    def identifier(self, value, label, seen):
        if not self.string(value, label):
            return False
        if value in seen:
            self.error(f"{label}: duplicate ID {value!r}")
        seen.add(value)
        return True

    def file(self, value, label):
        if not self.string(value, label):
            return None
        normalized = value.replace("\\", "/")
        windows = PureWindowsPath(value)
        if (windows.drive or windows.root or normalized.startswith("/")
                or ".." in normalized.split("/") or ":" in normalized or "\0" in normalized):
            self.error(f"{label} must be a workspace-relative path without traversal")
            return None
        try:
            candidate = (self.root / normalized).resolve(strict=True)
            if not candidate.is_relative_to(self.root):
                self.error(f"{label} resolves outside workspace")
                return None
            if not candidate.is_file():
                self.error(f"{label} must reference an existing regular file")
                return None
            return candidate
        except (OSError, RuntimeError, ValueError) as exc:
            self.error(f"{label} does not exist or cannot be resolved: {exc}")
            return None

    def files(self, value, label, nonempty=False):
        files = self.seq(value, label, nonempty)
        seen = set()
        for index, file_path in enumerate(files):
            if isinstance(file_path, str):
                if file_path in seen:
                    self.error(f"{label}: duplicate file path {file_path!r}")
                seen.add(file_path)
            self.file(file_path, f"{label}[{index}]")

    def https(self, value, label):
        if not self.string(value, label):
            return
        try:
            parsed = urlsplit(value)
            valid = (parsed.scheme == "https" and parsed.hostname
                     and not parsed.username and not parsed.password
                     and not any(character.isspace() or ord(character) < 32 for character in value))
            parsed.port  # Also reject malformed port syntax.
        except ValueError:
            valid = False
        if not valid:
            self.error(f"{label} must be an HTTPS URL with a hostname and no embedded credentials")


def validate_receipt(receipt, root):
    """Return validation errors. Never execute commands or contact remote URLs."""
    try:
        workspace = Path(root).resolve(strict=True)
        if not workspace.is_dir():
            return ["workspace root must be an existing directory"]
    except (TypeError, ValueError, OSError, RuntimeError) as exc:
        return [f"workspace root must be an existing directory: {exc}"]

    check = _Validation(workspace)
    data = check.obj(receipt, "receipt", (
        "schema_version", "status", "source", "units", "required_checks",
        "checks", "review", "blockers", "delivery",
    ))
    if type(data.get("schema_version")) is not int or data.get("schema_version") != 1:
        check.error("schema_version must be integer 1")
    check.enum(data.get("status"), "status", ("complete", "blocked", "failed"))
    if data.get("status") != "complete":
        check.error("receipt status must be complete to pass this completion check")

    source = check.obj(data.get("source"), "source", ("path", "sha256"))
    source_path = check.file(source.get("path"), "source.path")
    source_hash = source.get("sha256")
    valid_hash = isinstance(source_hash, str) and re.fullmatch(r"[0-9a-fA-F]{64}", source_hash)
    if not valid_hash:
        check.error("source.sha256 must contain exactly 64 hexadecimal characters")
    elif source_path:
        try:
            with source_path.open("rb") as stream:
                digest = hashlib.sha256()
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
                actual_hash = digest.hexdigest()
            if actual_hash != source_hash.lower():
                check.error("source.sha256 does not match the current source file")
        except OSError as exc:
            check.error(f"source.path cannot be read: {exc}")

    unit_ids = set()
    for index, item in enumerate(check.seq(data.get("units"), "units", nonempty=True)):
        label = f"units[{index}]"
        unit = check.obj(item, label, ("id", "status", "files"))
        check.identifier(unit.get("id"), f"{label}.id", unit_ids)
        check.enum(unit.get("status"), f"{label}.status", ("complete", "planned", "blocked", "failed"))
        if unit.get("status") != "complete":
            check.error(f"{label} must be complete")
        check.files(unit.get("files"), f"{label}.files", nonempty=True)

    required_ids = set()
    for index, identifier in enumerate(check.seq(data.get("required_checks"), "required_checks", nonempty=True)):
        check.identifier(identifier, f"required_checks[{index}]", required_ids)

    checks_by_id = {}
    check_ids = set()
    for index, item in enumerate(check.seq(data.get("checks"), "checks")):
        label = f"checks[{index}]"
        result = check.obj(item, label, ("id", "status", "command", "exit_code", "evidence"), ("reason",))
        if check.identifier(result.get("id"), f"{label}.id", check_ids):
            checks_by_id[result["id"]] = result
        check.enum(result.get("status"), f"{label}.status", ("passed", "failed", "skipped"))
        check.string(result.get("command"), f"{label}.command")
        exit_code = result.get("exit_code")
        if exit_code is not None and type(exit_code) is not int:
            check.error(f"{label}.exit_code must be an integer or null, never a boolean")
        if result.get("status") == "passed" and (type(exit_code) is not int or exit_code != 0):
            check.error(f"{label}.exit_code must be integer 0 for a passed check")
        check.files(result.get("evidence"), f"{label}.evidence", nonempty=result.get("status") == "passed")
        if "reason" in result or result.get("status") == "skipped":
            check.string(result.get("reason"), f"{label}.reason")

    for identifier in sorted(required_ids):
        result = checks_by_id.get(identifier)
        if result is None:
            check.error(f"required check {identifier!r} is missing")
        elif result.get("status") != "passed" or type(result.get("exit_code")) is not int or result.get("exit_code") != 0:
            check.error(f"required check {identifier!r} must have passed with exit_code 0")

    review = check.obj(data.get("review"), "review", ("status", "findings"), ("reason",))
    check.enum(review.get("status"), "review.status", ("complete", "unavailable"))
    if review.get("status") != "complete":
        check.error("review must be complete; unavailable review cannot support completion")
    if "reason" in review or review.get("status") == "unavailable":
        check.string(review.get("reason"), "review.reason")
    finding_ids = set()
    for index, item in enumerate(check.seq(review.get("findings"), "review.findings")):
        label = f"review.findings[{index}]"
        finding = check.obj(item, label, ("id", "severity", "status"))
        check.identifier(finding.get("id"), f"{label}.id", finding_ids)
        check.enum(finding.get("severity"), f"{label}.severity", ("blocking", "nonblocking"))
        check.enum(finding.get("status"), f"{label}.status", ("resolved", "open"))
        if finding.get("severity") == "blocking" and finding.get("status") == "open":
            check.error(f"{label}: blocking finding is still open")

    blockers = check.seq(data.get("blockers"), "blockers")
    for index, blocker in enumerate(blockers):
        check.string(blocker, f"blockers[{index}]")
    if blockers:
        check.error("blockers must be empty before completion")

    delivery = check.obj(data.get("delivery"), "delivery", ("mode", "status", "evidence"), ("url",))
    check.enum(delivery.get("mode"), "delivery.mode", ("local", "pull_request", "deployed"))
    check.enum(delivery.get("status"), "delivery.status", ("complete", "pending"))
    if delivery.get("status") != "complete":
        check.error("delivery must be complete")
    check.files(delivery.get("evidence"), "delivery.evidence", nonempty=True)
    if delivery.get("mode") in ("pull_request", "deployed") or "url" in delivery:
        check.https(delivery.get("url"), "delivery.url")
    return check.errors


def _unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path, help="JSON completion receipt")
    parser.add_argument("--root", required=True, type=Path, help="Existing workspace directory for all artifact paths")
    parser.add_argument("--json", action="store_true", help="Print machine-readable validation results")
    args = parser.parse_args(argv)
    try:
        with args.receipt.open("r", encoding="utf-8-sig") as stream:
            receipt = json.load(stream, object_pairs_hook=_unique_json_object)
        errors = validate_receipt(receipt, args.root)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        errors = [f"Cannot read receipt: {exc}"]
    if args.json:
        print(json.dumps({"valid": not errors, "errors": errors, "scope": SCOPE}, ensure_ascii=False))
    elif errors:
        print("Receipt does not establish completion:")
        for error in errors:
            print(f"- {error}")
        print(SCOPE)
    else:
        print("Receipt is complete with locally available evidence.")
        print(SCOPE)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
