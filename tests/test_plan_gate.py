import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/all-in-one/scripts/plan_gate.py"
spec = importlib.util.spec_from_file_location("plan_gate", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class PlanGateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "contract.md").write_text("A backend must reject duplicate effects.\n")
        self.plan = {
            "schema_version": 1, "status": "ready",
            "source": {"path": "contract.md", "sha256": hashlib.sha256((self.root / "contract.md").read_bytes()).hexdigest()},
            "requirements": [{"id": "R1", "text": "Duplicate effects are rejected."}],
            "units": [{"id": "U1", "requirement_ids": ["R1"], "depends_on": [], "owner": "worker-1", "files": ["service/new.py"], "verification_ids": ["V1"]}],
            "verification": [{"id": "V1", "unit_ids": ["U1"], "command": "python -m unittest", "assertions": ["Two deliveries produce one committed effect."]}],
            "binding_decisions": [], "blockers": [],
        }

    def errors(self, plan=None):
        return gate.validate_plan(self.plan if plan is None else plan, self.root)

    def rejects(self, fragment):
        self.assertTrue(any(fragment in error for error in self.errors()), self.errors())

    def add_unit(self, file="service/second.py"):
        self.plan["units"].append({"id": "U2", "requirement_ids": ["R1"], "depends_on": [], "owner": "worker-2", "files": [file], "verification_ids": ["V1"]})
        self.plan["verification"][0]["unit_ids"].append("U2")

    def test_accepts_new_contained_files_without_creating_them(self):
        self.assertEqual([], self.errors())
        self.assertFalse((self.root / "service").exists())

    def test_accepts_concrete_canonical_agent_owner(self):
        self.plan["units"][0]["owner"] = "/root/worker_1"
        self.assertEqual([], self.errors())

    def test_accepts_transitive_ordered_handoff(self):
        self.add_unit("service/new.py")
        self.plan["units"].append({"id": "U3", "requirement_ids": ["R1"], "depends_on": ["U1"], "owner": "worker-3", "files": ["service/third.py"], "verification_ids": ["V1"]})
        self.plan["verification"][0]["unit_ids"].append("U3")
        self.plan["units"][1]["depends_on"] = ["U3"]
        for unit in self.plan["units"]:
            unit["ownership_note"] = "U1 establishes API; U3 updates consumer; U2 follows both."
        self.assertEqual([], self.errors())

    def test_rejects_stale_source(self):
        (self.root / "contract.md").write_text("Changed requirement.")
        self.rejects("does not match")

    def test_rejects_missing_r_u_v_arrays(self):
        for key in ("requirements", "units", "verification"):
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan)
                del plan[key]
                self.assertTrue(gate.validate_plan(plan, self.root))

    def test_rejects_uncovered_requirement(self):
        self.plan["requirements"].append({"id": "R2", "text": "Tenant isolation."})
        self.rejects("R2 is not covered")

    def test_rejects_unknown_requirement(self):
        self.plan["units"][0]["requirement_ids"] = ["R3"]
        self.rejects("unknown requirement R3")

    def test_rejects_unknown_verification_and_unit(self):
        self.plan["units"][0]["verification_ids"] = ["V2"]
        self.plan["verification"][0]["unit_ids"] = ["U4"]
        self.rejects("unknown verification")
        self.rejects("unknown unit")

    def test_rejects_one_way_coverage(self):
        self.add_unit()
        self.plan["verification"][0]["unit_ids"].remove("U2")
        self.rejects("bidirectional")

    def test_rejects_unknown_dependency(self):
        self.plan["units"][0]["depends_on"] = ["U3"]
        self.rejects("unknown dependency")

    def test_rejects_self_cycle_and_multi_unit_cycle(self):
        self.plan["units"][0]["depends_on"] = ["U1"]
        self.rejects("cycle")
        self.add_unit()
        self.plan["units"][0]["depends_on"] = ["U2"]
        self.plan["units"][1]["depends_on"] = ["U1"]
        self.rejects("cycle")

    def test_rejects_unordered_shared_file(self):
        self.add_unit("service/new.py")
        for unit in self.plan["units"]:
            unit["ownership_note"] = "Controller integrates sequential changes."
        self.rejects("dependency ordering")

    def test_rejects_planned_file_parent_collision_even_when_ordered(self):
        self.add_unit("service/new.py/child.py")
        self.plan["units"][1]["depends_on"] = ["U1"]
        for unit in self.plan["units"]:
            unit["ownership_note"] = "An ordering note cannot make a file a directory."
        self.rejects("conflict as file/parent")

    @unittest.skipUnless(os.name == "nt", "Windows filesystem alias rules")
    def test_rejects_windows_aliases_and_reserved_devices(self):
        for path in (".git./config", ".git /config", "NUL", "folder/CON.py", "folder/AUX.txt", "folder/COM1", "folder/file. "):
            with self.subTest(path=path):
                self.plan["units"][0]["files"] = [path]
                self.rejects("Windows path alias or reserved")

    @unittest.skipUnless(os.name == "nt", "Windows filesystem alias rules")
    def test_rejects_windows_reserved_device_variants(self):
        for path in ("COM¹.py", "folder/COM².txt", "folder/COM³.log",
                     "folder/LPT¹.py", "LPT².txt", "folder/LPT³.log",
                     "NUL .txt", "folder/CON .py", "folder/COM1 .log"):
            with self.subTest(path=path):
                self.plan["units"][0]["files"] = [path]
                self.rejects("Windows path alias or reserved")

    @unittest.skipUnless(os.name == "nt", "Windows filesystem filename rules")
    def test_rejects_windows_invalid_characters_and_controls(self):
        for character in '<>"|' + ''.join(chr(value) for value in range(32)):
            with self.subTest(character=repr(character)):
                self.plan["units"][0]["files"] = ["folder/a" + character + "b.py"]
                self.assertTrue(self.errors())

    def test_accepts_valid_unicode_planned_file(self):
        self.plan["units"][0]["files"] = ["service/café_日本語_¹.py"]
        self.assertEqual([], self.errors())
        self.assertFalse((self.root / "service").exists())

    def test_rejects_unexplained_ordered_shared_file(self):
        self.add_unit("service/new.py")
        self.plan["units"][1]["depends_on"] = ["U1"]
        self.plan["units"][0]["ownership_note"] = "First edit establishes API."
        self.rejects("on both units")

    def test_accepts_ordered_explained_handoff(self):
        self.add_unit("service/new.py")
        self.plan["units"][1]["depends_on"] = ["U1"]
        for unit in self.plan["units"]:
            unit["ownership_note"] = "U1 establishes the API; U2 adds recovery after U1."
        self.assertEqual([], self.errors())

    def test_rejects_invalid_owner(self):
        for owner in (None, [], "", "unassigned", "worker one", "<owner>"):
            with self.subTest(owner=owner):
                self.plan["units"][0]["owner"] = owner
                self.rejects("owner")

    def test_rejects_unsafe_ownership(self):
        for path in ("../outside.py", "C:/outside.py", "/outside.py", ".git/config", "service/*.py", ".", "contract.md/child.py"):
            with self.subTest(path=path):
                self.plan["units"][0]["files"] = [path]
                if path == "contract.md/child.py":
                    # A path below an existing regular file cannot be a creatable artifact.
                    self.assertTrue(self.errors())
                else:
                    self.assertTrue(self.errors())

    def test_rejects_empty_commands_and_assertions(self):
        for key, value in (("command", ""), ("assertions", []), ("assertions", [""])):
            with self.subTest(key=key, value=value):
                self.plan["verification"][0][key] = value
                self.assertTrue(self.errors())

    def test_rejects_blockers_and_unresolved_decisions(self):
        self.plan["binding_decisions"] = [{"id": "D1", "status": "unresolved", "resolution": "Database durability is unspecified."}]
        self.plan["blockers"] = ["Durability target missing."]
        self.rejects("unresolved binding decision")
        self.rejects("blockers must be empty")

    def test_rejects_duplicates_and_unknown_fields(self):
        self.plan["requirements"].append(copy.deepcopy(self.plan["requirements"][0]))
        self.plan["unexpected"] = True
        self.rejects("duplicate ID")
        self.rejects("unknown field")

    def test_malformed_types_do_not_crash(self):
        for value in (None, [], 1, "plan", {"schema_version": True}):
            with self.subTest(value=value):
                self.assertTrue(gate.validate_plan(value, self.root))

    def test_metadata_has_explicit_types(self):
        self.plan["context"] = {"stack": ["Python"]}
        self.plan["architecture"] = {"recovery": "Durable idempotent writes."}
        self.plan["reviews"] = [{"reviewer": "independent", "status": "planned"}]
        self.plan["risks"] = ["Provider idempotency window."]
        self.assertEqual([], self.errors())
        self.plan["verification"][0]["failure_expected"] = "false"
        self.rejects("must be boolean")

    def test_cli_rejects_duplicate_json_keys(self):
        path = self.root / "plan.json"
        path.write_text('{"schema_version":1,"schema_version":1}')
        result = subprocess.run([sys.executable, str(SCRIPT), str(path), "--root", str(self.root), "--json"], capture_output=True, text=True)
        self.assertEqual(1, result.returncode)
        self.assertIn("duplicate JSON key", json.loads(result.stdout)["errors"][0])

    def test_cli_returns_scoped_success_and_does_not_execute_command(self):
        self.plan["verification"][0]["command"] = "create a forbidden marker"
        path = self.root / "plan.json"
        path.write_text(json.dumps(self.plan))
        before = set(self.root.rglob("*"))
        result = subprocess.run([sys.executable, str(SCRIPT), str(path), "--root", str(self.root), "--json"], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["valid"])
        self.assertIn("does not authenticate", payload["scope"])
        self.assertEqual(before, set(self.root.rglob("*")))


if __name__ == "__main__":
    unittest.main()
