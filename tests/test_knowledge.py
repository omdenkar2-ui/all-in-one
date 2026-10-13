"""Behavior tests for the offline knowledge library; all mutations use fixtures."""

from contextlib import closing
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "all-in-one" / "scripts" / "knowledge.py"


class KnowledgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="All in One knowledge ")
        self.skill = Path(self.temp.name) / "skill with spaces"
        self.data = self.skill / "knowledge"
        self.data.mkdir(parents=True)
        references = self.skill / "references"
        references.mkdir()
        (references / "agents.md").write_text("Recovery playbook\n", encoding="utf-8")
        (references / "data.md").write_text("Data playbook\n", encoding="utf-8")
        self.sources = {
            "schema_version": 1,
            "reviewed_on": "2026-10-05",
            "sources": [{"id": "temporal", "name": "Temporal", "url": "https://github.com/temporalio/skill-temporal-developer", "license": "MIT"}],
        }
        self.patterns = {
            "schema_version": 1,
            "patterns": [
                self.pattern("recovery", "agents", "Checkpoint recovery and idempotency", "A workflow restart repeats a payment side effect.", "references/agents.md"),
                self.pattern("indexing", "data", "Measured query indexes", "A query reads too many database rows.", "references/data.md"),
            ],
        }
        self.write_json()

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def pattern(identifier, domain, title, problem, playbook):
        return {"id": identifier, "domain": domain, "title": title, "problem": problem, "when_to_use": "When repeated work must be safe.", "approach": "Use a stable key and persist the outcome.", "failure_modes": ["Retrying with a fresh key repeats an external effect."], "verification": ["Inject a restart and assert one effect."], "source_ids": ["temporal"], "playbook": playbook}

    def write_json(self):
        (self.data / "sources.json").write_text(json.dumps(self.sources), encoding="utf-8")
        (self.data / "backend-knowledge.json").write_text(json.dumps(self.patterns), encoding="utf-8")

    def run_cli(self, *arguments, expected=0, script=SCRIPT, data=None):
        result = subprocess.run([sys.executable, str(script), "--data-dir", str(data or self.data), *arguments], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
        return result

    def test_build_search_and_check_preserve_provenance(self):
        self.run_cli("build")
        result = json.loads(self.run_cli("search", "checkpoint recovery idempotency", "--json").stdout)
        self.assertEqual("recovery", result[0]["id"])
        self.assertEqual("references/agents.md", result[0]["playbook"])
        self.assertEqual(self.sources["sources"][0]["url"], result[0]["sources"][0]["url"])
        self.assertIn("Inject a restart", result[0]["verification"][0])
        self.run_cli("check")

    def test_failed_replacement_preserves_existing_index_and_cleans_temporary_file(self):
        self.run_cli("build")
        database = self.data / "backend-knowledge.sqlite"
        original = database.read_bytes()
        original_files = set(self.data.iterdir())
        spec = importlib.util.spec_from_file_location("all_in_one_knowledge_failure_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with patch.object(module.os, "replace", side_effect=OSError("simulated replacement failure")):
            with self.assertRaises(OSError):
                module.build(self.data, force=True)
        self.assertEqual(original, database.read_bytes())
        self.assertEqual(original_files, set(self.data.iterdir()))
        self.run_cli("check")
        matches = json.loads(self.run_cli("search", "recovery", "--json").stdout)
        self.assertEqual("recovery", matches[0]["id"])

    def test_sources_work_without_database_and_data_dir_after_command(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "sources", "--json", "--data-dir", str(self.data)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(self.sources["sources"], json.loads(result.stdout))
        self.assertFalse((self.data / "backend-knowledge.sqlite").exists())

    def test_build_refuses_replacement_without_force_and_force_updates(self):
        self.run_cli("build")
        before = (self.data / "backend-knowledge.sqlite").read_bytes()
        self.patterns["patterns"][0]["title"] = "Durable recovery"
        self.write_json()
        self.assertIn("--force", self.run_cli("build", expected=1).stderr)
        self.assertEqual(before, (self.data / "backend-knowledge.sqlite").read_bytes())
        self.run_cli("check", expected=1)
        self.run_cli("build", "--force")
        self.run_cli("check")

    def test_malformed_sources_and_patterns_are_rejected(self):
        changes = [
            lambda: self.sources["sources"].append(dict(self.sources["sources"][0])),
            lambda: self.patterns["patterns"].append(dict(self.patterns["patterns"][0])),
            lambda: self.patterns["patterns"][0].update(domain="frontend"),
            lambda: self.patterns["patterns"][0].update(source_ids=["unknown"]),
            lambda: self.patterns["patterns"][0].update(verification=[]),
            lambda: self.patterns["patterns"][0].update(title="   "),
            lambda: self.sources.update(schema_version=True),
            lambda: self.sources["sources"][0].update(url="file:///private"),
            lambda: self.sources["sources"][0].update(url="https://[invalid"),
        ]
        original_sources = json.dumps(self.sources)
        original_patterns = json.dumps(self.patterns)
        for change in changes:
            with self.subTest(change=change):
                self.sources = json.loads(original_sources)
                self.patterns = json.loads(original_patterns)
                change()
                self.write_json()
                self.run_cli("build", expected=1)
                self.assertFalse((self.data / "backend-knowledge.sqlite").exists())

    def test_duplicate_json_keys_are_rejected(self):
        (self.data / "sources.json").write_text('{"schema_version":1,"schema_version":1,"sources":[]}', encoding="utf-8")
        self.assertIn("duplicate", self.run_cli("build", expected=1).stderr.lower())

    def test_nonfinite_json_numbers_are_rejected(self):
        self.sources["sources"][0]["extra_number"] = float("nan")
        self.write_json()
        self.assertIn("Invalid JSON number", self.run_cli("build", expected=1).stderr)

    def test_missing_and_escaping_playbooks_are_rejected(self):
        for playbook in ["references/missing.md", "../private.md", "references/../../private.md", "C:/private.md", "references\\agents.md"]:
            with self.subTest(playbook=playbook):
                self.patterns["patterns"][0]["playbook"] = playbook
                self.write_json()
                self.run_cli("build", expected=1)
                self.assertFalse((self.data / "backend-knowledge.sqlite").exists())

    def test_symlink_escape_is_rejected_when_supported(self):
        outside = Path(self.temp.name) / "outside.md"
        outside.write_text("Outside\n", encoding="utf-8")
        link = self.skill / "references" / "outside.md"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("Creating symlinks is unavailable on this host.")
        self.patterns["patterns"][0]["playbook"] = "references/outside.md"
        self.write_json()
        self.run_cli("build", expected=1)

    def test_search_is_read_only_and_sql_query_is_data(self):
        self.run_cli("build")
        database = self.data / "backend-knowledge.sqlite"
        before = database.read_bytes()
        self.assertEqual([], json.loads(self.run_cli("search", "'; DROP TABLE patterns; --", "--json").stdout))
        self.run_cli("check")
        self.assertEqual(before, database.read_bytes())

    def test_domain_filter_limit_and_stable_tie_order(self):
        self.patterns["patterns"].append(self.pattern("aaa", "agents", "Checkpoint recovery and idempotency", self.patterns["patterns"][0]["problem"], "references/agents.md"))
        self.write_json()
        self.run_cli("build")
        result = json.loads(self.run_cli("search", "checkpoint", "--domain", "agents", "--limit", "1", "--json").stdout)
        self.assertEqual(["aaa"], [item["id"] for item in result])
        self.assertEqual([], json.loads(self.run_cli("search", "checkpoint", "--domain", "data", "--json").stdout))
        self.run_cli("search", "checkpoint", "--limit", "0", expected=2)
        self.run_cli("search", "checkpoint", "--limit", "101", expected=2)
        self.run_cli("search", "checkpoint", "--domain", "frontend", expected=2)

    def test_matching_distinct_terms_outranks_repeating_one_term(self):
        recovery, indexing = self.patterns["patterns"]
        recovery["title"] = "Durable effects"
        recovery["problem"] = "Idempotency enables recovery after a crash."
        for key in ("title", "problem", "when_to_use", "approach"):
            indexing[key] = "Recovery recovery recovery"
        self.write_json()
        self.run_cli("build")
        result = json.loads(self.run_cli("search", "recovery idempotency", "--json").stdout)
        self.assertEqual("recovery", result[0]["id"])

    def test_common_word_forms_match_the_same_concept(self):
        self.run_cli("build")
        result = json.loads(self.run_cli("search", "idempotent", "--json").stdout)
        self.assertEqual("recovery", result[0]["id"])

    def test_missing_database_and_empty_query_fail_usefully(self):
        self.assertIn("build", self.run_cli("search", "checkpoint", expected=1).stderr)
        self.run_cli("build")
        self.run_cli("search", "!!!", expected=1)
        self.run_cli("search", "the and a", expected=1)

    def test_corruption_and_semantic_changes_are_detected(self):
        self.run_cli("build")
        database = self.data / "backend-knowledge.sqlite"
        with closing(sqlite3.connect(database)) as connection, connection:
            connection.execute("UPDATE patterns SET record_json = '{}' WHERE id = ?", ("recovery",))
        self.run_cli("check", expected=1)
        database.write_bytes(b"This is not SQLite")
        self.run_cli("check", expected=1)

    def test_full_package_relocation_keeps_default_paths_working(self):
        scripts = self.skill / "scripts"
        scripts.mkdir()
        shutil.copy2(SCRIPT, scripts / "knowledge.py")
        self.run_cli("build")
        moved = Path(self.temp.name) / "relocated package with spaces"
        shutil.copytree(self.skill, moved)
        for arguments in [("check",), ("search", "idempotency", "--json"), ("build", "--force")]:
            result = subprocess.run([sys.executable, str(moved / "scripts" / "knowledge.py"), *arguments], cwd=self.temp.name, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
