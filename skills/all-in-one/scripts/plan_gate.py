"""Validate structural readiness of a backend plan without executing its commands.

Coverage, ownership, dependency order and source identity are mechanical checks.
Passing does not establish semantic completeness, test quality or executed proof.
"""

import argparse
from collections import deque
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PureWindowsPath
import re
import sys


_spec = importlib.util.spec_from_file_location(
    "_aio_receipt_core", Path(__file__).with_name("check_receipt.py"))
_core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_core)
SCOPE = ("Checks source identity, R/U/V links, dependency order and declared file "
         "ownership only; does not authenticate execution or prove plan semantics.")


class _PlanValidation(_core._Validation):
    def owned_path(self, value, label, directory=False):
        if not self.string(value, label):
            return None
        normalized = value.replace("\\", "/")
        windows = PureWindowsPath(value)
        parts = normalized.split("/")
        if (windows.drive or windows.root or normalized.startswith("/")
                or ".." in parts or ":" in normalized or "\0" in normalized
                or any(c in normalized for c in "*?[]")
                or any(part.casefold() == ".git" for part in parts)):
            self.error(f"{label} must be an exact contained relative path without traversal, .git or globs")
            return None
        reserved = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
        reserved.update(f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10))
        reserved.update(f"{prefix}{number}" for prefix in ("COM", "LPT") for number in "¹²³")
        if os.name == "nt" and any(
                part.endswith((".", " "))
                or part.split(".", 1)[0].rstrip(" ").upper() in reserved
                or any(character in '<>"|' or ord(character) < 32 for character in part)
                for part in parts if part):
            self.error(f"{label} uses a Windows path alias or reserved device name or invalid filename character")
            return None
        try:
            candidate = (self.root / normalized).resolve()
            if not candidate.is_relative_to(self.root) or candidate == self.root:
                self.error(f"{label} resolves outside workspace or to its root")
                return None
            if any(part.casefold() == ".git" for part in candidate.relative_to(self.root).parts):
                self.error(f"{label} resolves into protected .git metadata")
                return None
            if candidate.exists() and candidate.is_dir() != directory:
                self.error(f"{label} must identify a {'directory' if directory else 'file'}")
                return None
            if any(parent.exists() and not parent.is_dir()
                   for parent in candidate.parents if parent != self.root):
                self.error(f"{label} has an existing file as its parent")
                return None
            return candidate
        except (OSError, RuntimeError, ValueError) as error:
            self.error(f"{label} cannot be resolved: {error}")
            return None

    def ids(self, value, label, prefix=None, nonempty=True):
        result = set()
        for index, item in enumerate(self.seq(value, label, nonempty)):
            if self.identifier(item, f"{label}[{index}]", result) and prefix:
                if not re.fullmatch(prefix + r"[1-9]\d*", item):
                    self.error(f"{label}[{index}] must use a stable {prefix} number")
        return result

    def record_id(self, value, label, prefix, seen):
        if not self.identifier(value, label, seen):
            return None
        if not re.fullmatch(prefix + r"[1-9]\d*", value):
            self.error(f"{label} must use a stable {prefix} number")
        return value

    def strings(self, value, label, nonempty=True):
        for index, item in enumerate(self.seq(value, label, nonempty)):
            self.string(item, f"{label}[{index}]")


def validate_plan(plan, root):
    """Return all supported structural failures; never execute plan commands."""
    try:
        workspace = Path(root).resolve(strict=True)
        if not workspace.is_dir():
            return ["workspace root must be an existing directory"]
    except (TypeError, ValueError, OSError, RuntimeError) as error:
        return [f"workspace root must be an existing directory: {error}"]
    check = _PlanValidation(workspace)
    data = check.obj(plan, "plan", (
        "schema_version", "status", "source", "requirements", "units",
        "verification", "binding_decisions", "blockers",
    ), ("context", "architecture", "reviews", "risks"))
    if type(data.get("schema_version")) is not int or data.get("schema_version") != 1:
        check.error("schema_version must be integer 1")
    check.enum(data.get("status"), "status", ("ready", "blocked"))
    if data.get("status") != "ready":
        check.error("plan status must be ready to pass the execution-readiness gate")
    source = check.obj(data.get("source"), "source", ("path", "sha256"))
    source_path = check.file(source.get("path"), "source.path")
    source_hash = source.get("sha256")
    if not isinstance(source_hash, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", source_hash):
        check.error("source.sha256 must contain exactly 64 hexadecimal characters")
    elif source_path:
        try:
            digest = hashlib.sha256()
            with source_path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            if digest.hexdigest() != source_hash.lower():
                check.error("source.sha256 does not match the current source file")
        except OSError as error:
            check.error(f"source.path cannot be read: {error}")

    requirements = set()
    for index, item in enumerate(check.seq(data.get("requirements"), "requirements", True)):
        label = f"requirements[{index}]"
        item = check.obj(item, label, ("id", "text"))
        check.record_id(item.get("id"), f"{label}.id", "R", requirements)
        check.string(item.get("text"), f"{label}.text")

    units = {}
    unit_ids = set()
    owned = {}
    for index, item in enumerate(check.seq(data.get("units"), "units", True)):
        label = f"units[{index}]"
        unit = check.obj(item, label, (
            "id", "requirement_ids", "depends_on", "owner", "files", "verification_ids",
        ), ("title", "inputs", "outputs", "test_first", "acceptance", "ownership_note"))
        identifier = check.record_id(unit.get("id"), f"{label}.id", "U", unit_ids)
        check.string(unit.get("owner"), f"{label}.owner")
        if isinstance(unit.get("owner"), str) and not re.fullmatch(r"/?[A-Za-z0-9][A-Za-z0-9_.:/-]*", unit["owner"]):
            check.error(f"{label}.owner must name one concrete owner without whitespace or placeholders")
        if str(unit.get("owner", "")).casefold() in ("unassigned", "tbd", "todo", "unknown"):
            check.error(f"{label}.owner is not assigned")
        reqs = check.ids(unit.get("requirement_ids"), f"{label}.requirement_ids", "R")
        deps = check.ids(unit.get("depends_on"), f"{label}.depends_on", "U", False)
        verifications = check.ids(unit.get("verification_ids"), f"{label}.verification_ids", "V")
        files = set()
        for file_index, file_path in enumerate(check.seq(unit.get("files"), f"{label}.files", True)):
            resolved = check.owned_path(file_path, f"{label}.files[{file_index}]")
            if resolved:
                if resolved in files:
                    check.error(f"{label}.files repeats the same resolved file")
                files.add(resolved)
        for key in ("title", "test_first", "ownership_note"):
            if key in unit:
                check.string(unit[key], f"{label}.{key}")
        for key in ("inputs", "outputs", "acceptance"):
            if key in unit:
                check.strings(unit[key], f"{label}.{key}", nonempty=key == "acceptance")
        if identifier:
            units[identifier] = {"requirements": reqs, "dependencies": deps,
                                 "verification": verifications, "record": unit}
            for file_path in files:
                owned.setdefault(file_path, []).append(identifier)

    checks = {}
    verification_ids = set()
    for index, item in enumerate(check.seq(data.get("verification"), "verification", True)):
        label = f"verification[{index}]"
        item = check.obj(item, label, ("id", "unit_ids", "command", "assertions"),
                         ("cwd", "phase", "failure_expected"))
        identifier = check.record_id(item.get("id"), f"{label}.id", "V", verification_ids)
        mapped_units = check.ids(item.get("unit_ids"), f"{label}.unit_ids", "U")
        check.string(item.get("command"), f"{label}.command")
        check.strings(item.get("assertions"), f"{label}.assertions")
        if "cwd" in item:
            if item["cwd"] == ".":
                pass
            else:
                check.owned_path(item["cwd"], f"{label}.cwd", directory=True)
        if "phase" in item:
            check.string(item["phase"], f"{label}.phase")
        if "failure_expected" in item and type(item["failure_expected"]) is not bool:
            check.error(f"{label}.failure_expected must be boolean")
        if identifier:
            checks[identifier] = mapped_units

    covered_requirements = set()
    for identifier, unit in units.items():
        covered_requirements.update(unit["requirements"])
        for requirement in unit["requirements"] - requirements:
            check.error(f"{identifier} references unknown requirement {requirement}")
        for dependency in unit["dependencies"] - unit_ids:
            check.error(f"{identifier} references unknown dependency {dependency}")
        for verification in unit["verification"] - verification_ids:
            check.error(f"{identifier} references unknown verification {verification}")
        for verification in unit["verification"] & verification_ids:
            if identifier not in checks.get(verification, set()):
                check.error(f"{identifier}/{verification} coverage links must be bidirectional")
    for requirement in requirements - covered_requirements:
        check.error(f"requirement {requirement} is not covered by any unit")
    for identifier, mapped_units in checks.items():
        for unit_id in mapped_units - unit_ids:
            check.error(f"{identifier} references unknown unit {unit_id}")
        for unit_id in mapped_units & unit_ids:
            if identifier not in units[unit_id]["verification"]:
                check.error(f"{unit_id}/{identifier} coverage links must be bidirectional")

    pending = {identifier: len(unit["dependencies"] & unit_ids) for identifier, unit in units.items()}
    successors = {identifier: set() for identifier in units}
    for identifier, unit in units.items():
        for dependency in unit["dependencies"] & unit_ids:
            successors[dependency].add(identifier)
    queue = deque(identifier for identifier, count in pending.items() if count == 0)
    ordered = []
    ancestors = {identifier: set() for identifier in units}
    while queue:
        current = queue.popleft()
        ordered.append(current)
        for successor in successors[current]:
            ancestors[successor].update(ancestors[current] | {current})
            pending[successor] -= 1
            if pending[successor] == 0:
                queue.append(successor)
    if len(ordered) != len(units):
        check.error("unit dependencies contain a cycle")
    for file_path, owners in owned.items():
        for index, first in enumerate(owners):
            for second in owners[index + 1:]:
                if first not in ancestors[second] and second not in ancestors[first]:
                    check.error(f"conflicting ownership of {file_path.relative_to(workspace)} by {first}/{second} requires dependency ordering")
                if not all(isinstance(units[owner]["record"].get("ownership_note"), str)
                           and units[owner]["record"]["ownership_note"].strip() for owner in (first, second)):
                    check.error(f"shared ownership {first}/{second} requires ownership_note on both units")
    paths = sorted(owned)
    for index, first in enumerate(paths):
        for second in paths[index + 1:]:
            if first.is_relative_to(second) or second.is_relative_to(first):
                check.error(f"declared file paths {first.relative_to(workspace)} and {second.relative_to(workspace)} conflict as file/parent")

    decision_ids = set()
    for index, item in enumerate(check.seq(data.get("binding_decisions"), "binding_decisions")):
        label = f"binding_decisions[{index}]"
        item = check.obj(item, label, ("id", "status", "resolution"))
        check.record_id(item.get("id"), f"{label}.id", "D", decision_ids)
        check.enum(item.get("status"), f"{label}.status", ("resolved", "unresolved"))
        check.string(item.get("resolution"), f"{label}.resolution")
        if item.get("status") != "resolved":
            check.error(f"{label} is an unresolved binding decision")
    blockers = check.seq(data.get("blockers"), "blockers")
    check.strings(blockers, "blockers", False)
    if blockers:
        check.error("blockers must be empty before execution readiness")
    for key in ("context", "architecture"):
        if key in data and not isinstance(data[key], dict):
            check.error(f"{key} must be an object")
    if "reviews" in data:
        for index, review in enumerate(check.seq(data["reviews"], "reviews")):
            if not isinstance(review, dict):
                check.error(f"reviews[{index}] must be an object")
    if "risks" in data:
        check.strings(data["risks"], "risks", False)
    return sorted(check.errors)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        with args.plan.open(encoding="utf-8-sig") as stream:
            plan = json.load(stream, object_pairs_hook=_core._unique_json_object)
        errors = validate_plan(plan, args.root)
    except (OSError, UnicodeError, ValueError, RecursionError) as error:
        errors = [f"Cannot read plan: {error}"]
    if args.json:
        print(json.dumps({"valid": not errors, "errors": errors, "scope": SCOPE}))
    else:
        print("Plan is structurally ready." if not errors else "Plan is not ready:")
        for error in errors:
            print(f"- {error}")
        print(SCOPE)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
