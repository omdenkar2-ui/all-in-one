"""Failure cases for the local completion-evidence checker."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/all-in-one/scripts/check_receipt.py"
SPEC = importlib.util.spec_from_file_location("check_receipt", SCRIPT)
receipt_checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(receipt_checker)


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(prefix="all in one receipts ")
        self.root = Path(self.workspace.name)
        (self.root / "contract.md").write_text("Accept duplicate jobs safely.\n", encoding="utf-8")
        (self.root / "worker.py").write_text("# Implemented worker artifact.\n", encoding="utf-8")
        (self.root / "evidence").mkdir()
        (self.root / "evidence/tests.txt").write_text("Required checks passed.\n", encoding="utf-8")
        self.receipt = {
            "schema_version": 1,
            "status": "complete",
            "source": {
                "path": "contract.md",
                "sha256": hashlib.sha256((self.root / "contract.md").read_bytes()).hexdigest(),
            },
            "units": [{"id": "U1", "status": "complete", "files": ["worker.py"]}],
            "required_checks": ["unit", "failure"],
            "checks": [
                {"id": "unit", "status": "passed", "command": "python -m unittest", "exit_code": 0,
                 "evidence": ["evidence/tests.txt"]},
                {"id": "failure", "status": "passed", "command": "python failure_scenarios.py",
                 "exit_code": 0, "evidence": ["evidence/tests.txt"]},
            ],
            "review": {"status": "complete", "findings": []},
            "blockers": [],
            "delivery": {"mode": "local", "status": "complete", "evidence": ["worker.py"]},
        }

    def tearDown(self):
        self.workspace.cleanup()

    def errors(self, receipt=...):
        return receipt_checker.validate_receipt(self.receipt if receipt is ... else receipt, self.root)

    def assertRejected(self, fragment):
        errors = self.errors()
        self.assertTrue(errors, "Invalid evidence was accepted")
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_complete_local_receipt_passes(self):
        self.assertEqual([], self.errors())

    def test_failed_required_check_rejected(self):
        self.receipt["checks"][0].update(status="failed", exit_code=1)
        self.assertRejected("required check 'unit'")

    def test_skipped_required_check_rejected(self):
        self.receipt["checks"][0].update(status="skipped", exit_code=None, reason="Not run")
        self.assertRejected("required check 'unit'")

    def test_missing_required_check_rejected(self):
        self.receipt["checks"].pop()
        self.assertRejected("required check 'failure'")

    def test_duplicate_check_ids_rejected(self):
        self.receipt["checks"].append(copy.deepcopy(self.receipt["checks"][0]))
        self.assertRejected("duplicate")

    def test_duplicate_required_check_ids_rejected(self):
        self.receipt["required_checks"].append("unit")
        self.assertRejected("duplicate")

    def test_empty_required_checks_rejected(self):
        self.receipt["required_checks"] = []
        self.assertRejected("required_checks")

    def test_passed_check_with_nonzero_exit_rejected(self):
        self.receipt["checks"][0]["exit_code"] = 1
        self.assertRejected("exit_code")

    def test_boolean_exit_code_rejected(self):
        self.receipt["checks"][0]["exit_code"] = False
        self.assertRejected("exit_code")

    def test_empty_check_evidence_or_command_rejected(self):
        self.receipt["checks"][0].update(evidence=[], command=" ")
        self.assertRejected("checks[0]")

    def test_source_changed_after_receipt_rejected(self):
        (self.root / "contract.md").write_text("New acceptance requirement.\n", encoding="utf-8")
        self.assertRejected("sha256 does not match")

    def test_malformed_hash_rejected(self):
        self.receipt["source"]["sha256"] = "not-a-sha"
        self.assertRejected("sha256")

    def test_missing_artifact_rejected(self):
        self.receipt["units"][0]["files"] = ["missing.py"]
        self.assertRejected("does not exist")

    def test_directory_evidence_rejected(self):
        self.receipt["checks"][0]["evidence"] = ["evidence"]
        self.assertRejected("regular file")

    def test_path_traversal_rejected(self):
        self.receipt["delivery"]["evidence"] = ["../outside.txt"]
        self.assertRejected("relative")

    def test_absolute_and_windows_paths_rejected(self):
        for path in [str((self.root / "worker.py").resolve()), "C:\\worker.py", "C:worker.py",
                     "\\\\server\\share\\worker.py", "/worker.py", "evidence/../worker.py"]:
            with self.subTest(path=path):
                self.receipt["units"][0]["files"] = [path]
                self.assertRejected("relative")

    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory(prefix="all-in-one-outside-") as outside:
            target = Path(outside) / "outside.txt"
            target.write_text("Outside the selected root.\n", encoding="utf-8")
            link = self.root / "linked.txt"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"Symlinks unavailable: {exc}")
            self.receipt["delivery"]["evidence"] = ["linked.txt"]
            self.assertRejected("outside workspace")

    def test_incomplete_unit_and_receipt_rejected(self):
        self.receipt["status"] = "blocked"
        self.receipt["units"][0]["status"] = "blocked"
        self.assertRejected("must be complete")

    def test_duplicate_unit_ids_rejected(self):
        self.receipt["units"].append(copy.deepcopy(self.receipt["units"][0]))
        self.assertRejected("duplicate")

    def test_empty_units_rejected(self):
        self.receipt["units"] = []
        self.assertRejected("units")

    def test_complete_unit_needs_files(self):
        self.receipt["units"][0]["files"] = []
        self.assertRejected("units[0].files")

    def test_open_blocker_rejected(self):
        self.receipt["blockers"] = ["Replay compatibility is not verified."]
        self.assertRejected("blockers")

    def test_open_blocking_review_rejected(self):
        self.receipt["review"]["findings"] = [
            {"id": "F1", "severity": "blocking", "status": "open"}
        ]
        self.assertRejected("blocking finding")

    def test_resolved_blocking_and_open_nonblocking_review_passes(self):
        self.receipt["review"]["findings"] = [
            {"id": "F1", "severity": "blocking", "status": "resolved"},
            {"id": "F2", "severity": "nonblocking", "status": "open"},
        ]
        self.assertEqual([], self.errors())

    def test_unavailable_review_cannot_claim_complete(self):
        self.receipt["review"].update(status="unavailable", reason="Independent reviewer not run.")
        self.assertRejected("review must be complete")

    def test_remote_delivery_needs_https_url_and_local_evidence(self):
        self.receipt["delivery"] = {
            "mode": "pull_request", "status": "complete", "url": "http://example.com/pr/1", "evidence": []
        }
        self.assertRejected("HTTPS")
        self.assertRejected("evidence")

    def test_recorded_remote_claim_passes_without_authentication(self):
        self.receipt["delivery"] = {
            "mode": "deployed", "status": "complete", "url": "https://example.com/release/1",
            "evidence": ["evidence/tests.txt"],
        }
        self.assertEqual([], self.errors())

    def test_unsupported_delivery_mode_rejected(self):
        self.receipt["delivery"]["mode"] = "magic_proof"
        self.assertRejected("delivery.mode")

    def test_remote_url_rejects_credentials_and_malformed_authority(self):
        for url in ["https://user:password@example.com/release", "https://example.com:bad/release",
                    "https://example.com/space here", "https:///release"]:
            with self.subTest(url=url):
                self.receipt["delivery"].update(mode="deployed", url=url)
                self.assertRejected("HTTPS")

    def test_pending_delivery_rejected(self):
        self.receipt["delivery"]["status"] = "pending"
        self.assertRejected("delivery must be complete")

    def test_duplicate_json_keys_rejected_by_cli(self):
        receipt_file = self.root / "receipt.json"
        receipt_file.write_text('{"status":"complete","status":"blocked"}', encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(receipt_file), "--root", str(self.root), "--json"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("duplicate JSON key", json.loads(result.stdout)["errors"][0])

    def test_cli_success_json_and_scope(self):
        receipt_file = self.root / "receipt.json"
        receipt_file.write_text(json.dumps(self.receipt), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(receipt_file), "--root", str(self.root), "--json"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        output = json.loads(result.stdout)
        self.assertTrue(output["valid"])
        self.assertIn("not authenticate", output["scope"])

    def test_unknown_fields_and_duplicate_findings_rejected(self):
        self.receipt["completed"] = True
        self.receipt["review"]["findings"] = [
            {"id": "F1", "severity": "nonblocking", "status": "resolved"},
            {"id": "F1", "severity": "nonblocking", "status": "resolved"},
        ]
        self.assertRejected("unknown field")
        self.assertRejected("duplicate")

    def test_shipped_starter_cannot_claim_completion(self):
        template = SCRIPT.parent.parent / "templates/evidence-receipt.json"
        starter = json.loads(template.read_text(encoding="utf-8"))
        errors = self.errors(starter)
        self.assertTrue(any("status must be complete" in error for error in errors))
        self.assertTrue(any("sha256 does not match" in error for error in errors))

    def test_malformed_types_never_raise(self):
        cases = [None, [], "complete", {}, {"schema_version": True}]
        for field in self.receipt:
            candidate = copy.deepcopy(self.receipt)
            candidate[field] = False
            cases.append(candidate)
        for candidate in cases:
            with self.subTest(receipt=candidate):
                self.assertTrue(self.errors(candidate))

    def test_nested_malformed_types_never_raise(self):
        mutations = [
            ("units", [None]), ("checks", [None]),
            ("review", {"status": "complete", "findings": [None]}),
            ("delivery", {"mode": "local", "status": "complete", "evidence": "worker.py"}),
            ("source", {"path": [], "sha256": False}),
            ("required_checks", [False]), ("blockers", [False]),
        ]
        for field, value in mutations:
            candidate = copy.deepcopy(self.receipt)
            candidate[field] = value
            with self.subTest(field=field):
                self.assertTrue(self.errors(candidate))

    def test_missing_workspace_root_rejected(self):
        self.assertTrue(receipt_checker.validate_receipt(self.receipt, self.root / "missing"))


if __name__ == "__main__":
    unittest.main()
