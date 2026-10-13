import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/benchmark.py"
spec = importlib.util.spec_from_file_location("aio_benchmark", SCRIPT)
benchmark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)
EVALUATOR = '''import json, os
from pathlib import Path
value = json.loads(Path(os.environ["AIO_BENCHMARK_ARTIFACT"]).read_text())
print(json.dumps({"gates":{"correctness":True,"security":True,"recovery":True},"metrics":{"value":value["value"]},"notes":[]}))
'''


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="aio benchmark ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        (self.root / "task.md").write_text("Reject duplicate tenant-scoped jobs and recover after a crash.")
        (self.root / "evaluator.py").write_text(EVALUATOR)
        (self.root / "artifact.json").write_text('{"value":4}')
        self.definition = {
            "schema_version": 1, "status": "ready", "title": "Fixed backend test",
            "task": "task.md", "evaluator": "evaluator.py",
            "conditions": ["aio", "compound-engineering", "superpowers"],
            "trials": [{"id": "trial-1", "seed": 123}],
            "settings": {"model": "same-model", "reasoning": "same-effort", "tools": ["local"]},
            "gates": ["correctness", "security", "recovery"],
            "metrics": [{"id": "value", "direction": "lower"}],
            "assertions": ["Duplicate delivery preserves one effect; cross-tenant reads fail; restart recovers."],
        }
        self.definition_path = self.root / "definition.json"
        self.frozen = self.root / "frozen.json"

    def freeze(self):
        self.definition_path.write_text(json.dumps(self.definition))
        return benchmark.freeze(self.definition_path, self.root, self.frozen)

    def collect(self, condition="aio", output=None, timeout=10):
        return benchmark.collect(self.frozen, self.root, condition, "trial-1", "artifact.json",
                                 output or self.root / (condition + ".json"),
                                 [sys.executable, str(self.root / "evaluator.py")], timeout)

    def test_freeze_binds_task_evaluator_and_definition(self):
        frozen = self.freeze()
        self.assertEqual(benchmark.digest(self.root / "task.md"), frozen["task_sha256"])
        self.assertEqual(benchmark.digest(self.root / "evaluator.py"), frozen["evaluator_sha256"])
        self.assertEqual(benchmark.canonical_digest(self.definition), frozen["definition_sha256"])
        with self.assertRaises(FileExistsError):
            benchmark.freeze(self.definition_path, self.root, self.frozen)

    def test_stale_task_or_evaluator_rejected_before_execution(self):
        self.freeze()
        for path in ("task.md", "evaluator.py"):
            with self.subTest(path=path):
                original = (self.root / path).read_bytes()
                (self.root / path).write_bytes(original + b"\nchanged")
                with self.assertRaisesRegex(benchmark.BenchmarkError, "content changed"):
                    self.collect()
                self.assertFalse((self.root / "aio.json").exists())
                (self.root / path).write_bytes(original)

    def test_definition_cannot_hide_commands(self):
        self.definition["command"] = "create unauthorized output"
        with self.assertRaises(benchmark.BenchmarkError):
            self.freeze()

    def test_definition_rejects_single_duplicate_or_unsupported_conditions(self):
        for conditions in (["aio"], ["aio", "aio"],
                           ["aio", "compound-engineering", "compound-engineering"],
                           ["aio", "other"], ["aio", "../baseline"]):
            with self.subTest(conditions=conditions):
                definition = copy.deepcopy(self.definition)
                definition["conditions"] = conditions
                with self.assertRaisesRegex(benchmark.BenchmarkError, "2 or 3 unique supported IDs"):
                    benchmark.validate_definition(definition)

    def test_two_conditions_still_require_all_quality_gates(self):
        for gates in (["correctness", "security"], ["correctness", "security", "security"]):
            with self.subTest(gates=gates):
                definition = copy.deepcopy(self.definition)
                definition.update(conditions=["aio", "compound-engineering"], gates=gates)
                with self.assertRaisesRegex(benchmark.BenchmarkError, "correctness, security and recovery exactly once"):
                    benchmark.validate_definition(definition)

    def test_two_condition_freeze_collect_compare_retains_every_trial(self):
        self.definition["conditions"] = ["aio", "compound-engineering"]
        self.definition["trials"].append({"id": "trial-2", "seed": 456})
        frozen = self.freeze()
        self.assertEqual(["aio", "compound-engineering"], frozen["definition"]["conditions"])
        records = []
        for condition, first_value in (("aio", 4), ("compound-engineering", 7)):
            for offset, trial in enumerate(self.definition["trials"]):
                artifact = condition + "-" + trial["id"] + ".json"
                (self.root / artifact).write_text(json.dumps({"value": first_value + offset}))
                output = self.root / (condition + "-" + trial["id"] + "-result.json")
                record = benchmark.collect(self.frozen, self.root, condition, trial["id"], artifact,
                                           output, [sys.executable, str(self.root / "evaluator.py")])
                self.assertEqual([], record["errors"])
                self.assertEqual(trial["seed"], record["seed"])
                self.assertEqual({gate: True for gate in benchmark.GATES}, record["result"]["gates"])
                self.assertEqual(benchmark.digest(self.root / artifact), record["artifact_sha256"])
                records.append(output)
        with self.assertRaisesRegex(benchmark.BenchmarkError, "every declared"):
            benchmark.compare(self.frozen, self.root, records[:-1], self.root / "incomplete.json")
        self.assertFalse((self.root / "incomplete.json").exists())
        with self.assertRaisesRegex(benchmark.BenchmarkError, "condition was not declared"):
            self.collect("superpowers")
        report = benchmark.compare(self.frozen, self.root, records, self.root / "comparison.json")
        self.assertEqual(["aio", "compound-engineering"], [item["condition"] for item in report["conditions"]])
        self.assertTrue(all(item["eligible_for_metrics"] for item in report["conditions"]))
        self.assertEqual([4, 5], report["conditions"][0]["metrics"]["value"]["values"])
        self.assertEqual([7, 8], report["conditions"][1]["metrics"]["value"]["values"])
        self.assertEqual(2, report["conditions"][0]["metrics"]["value"]["count"])
        self.assertEqual(7.5, report["conditions"][1]["metrics"]["value"]["mean"])

    def test_missing_caller_argv_does_not_execute_anything(self):
        self.freeze()
        with self.assertRaisesRegex(benchmark.BenchmarkError, "explicit evaluator argv"):
            benchmark.collect(self.frozen, self.root, "aio", "trial-1", "artifact.json", self.root / "run.json", [])
        self.assertFalse((self.root / "run.json").exists())

    def test_other_evaluator_cannot_substitute(self):
        self.freeze()
        with self.assertRaisesRegex(benchmark.BenchmarkError, "frozen evaluator"):
            benchmark.collect(self.frozen, self.root, "aio", "trial-1", "artifact.json", self.root / "run.json", [sys.executable, "other.py"])

    def test_collect_executes_explicit_evaluator_with_observed_time_and_hashes(self):
        self.freeze()
        record = self.collect()
        self.assertEqual([], record["errors"])
        self.assertEqual(4, record["result"]["metrics"]["value"])
        self.assertEqual(benchmark.digest(self.root / "artifact.json"), record["artifact_sha256"])
        self.assertEqual(0, record["execution"]["exit_code"])
        self.assertGreater(record["execution"]["elapsed_seconds"], 0)
        self.assertIn("does not launch/attest", record["scope"])

    def test_collect_preserves_original_run(self):
        self.freeze()
        self.collect()
        original = (self.root / "aio.json").read_bytes()
        with self.assertRaisesRegex(benchmark.BenchmarkError, "preserve"):
            self.collect()
        self.assertEqual(original, (self.root / "aio.json").read_bytes())

    def test_undeclared_trial_or_condition_rejected(self):
        self.freeze()
        with self.assertRaisesRegex(benchmark.BenchmarkError, "condition"):
            self.collect("other")
        with self.assertRaisesRegex(benchmark.BenchmarkError, "trial"):
            benchmark.collect(self.frozen, self.root, "aio", "trial-2", "artifact.json", self.root / "run.json", [sys.executable, str(self.root / "evaluator.py")])

    def test_nonzero_exit_is_retained_and_not_success(self):
        (self.root / "evaluator.py").write_text(EVALUATOR + "raise SystemExit(2)\n")
        self.freeze()
        record = self.collect()
        self.assertIn("exited 2", record["errors"][0])
        self.assertIsNotNone(record["result"])
        self.assertEqual(2, record["execution"]["exit_code"])

    def test_timeout_is_recorded(self):
        (self.root / "evaluator.py").write_text("import time\ntime.sleep(30)\n")
        self.freeze()
        record = self.collect(timeout=0.1)
        self.assertTrue(record["execution"]["timed_out"])
        self.assertIn("timed out", record["errors"][0])

    def test_taskkill_timeout_still_kills_and_reaps_direct_child(self):
        process = mock.Mock(pid=12345, returncode=-9, stdout=io.BytesIO(b""), stderr=io.BytesIO(b""))
        process.wait.side_effect = [subprocess.TimeoutExpired("evaluator", 1), -9]
        process.poll.return_value = None
        with mock.patch.object(benchmark.os, "name", "nt"), mock.patch.object(benchmark.subprocess, "CREATE_NEW_PROCESS_GROUP", 512, create=True), mock.patch.object(benchmark.subprocess, "Popen", return_value=process), mock.patch.object(benchmark.subprocess, "run", side_effect=subprocess.TimeoutExpired("taskkill", 10)):
            record = benchmark.execute(["evaluator"], self.root, {}, 1)
        process.kill.assert_called_once()
        self.assertEqual(2, process.wait.call_count)
        self.assertTrue(record["timed_out"])
        self.assertTrue(record["cleanup_warnings"])

    def test_malformed_json_and_duplicate_keys_are_recorded(self):
        for text in ("not json", '{"gates":{},"gates":{}}'):
            with self.subTest(text=text):
                (self.root / "evaluator.py").write_text("print(" + repr(text) + ")\n")
                self.frozen.unlink(missing_ok=True)
                (self.root / "aio.json").unlink(missing_ok=True)
                self.freeze()
                self.assertTrue(self.collect()["errors"])

    def test_excessive_output_is_bounded_and_recorded(self):
        (self.root / "evaluator.py").write_text("import sys\nsys.stdout.write('x' * 1100000)\n")
        self.freeze()
        record = self.collect()
        self.assertEqual(1100000, record["execution"]["stdout_bytes"])
        self.assertEqual(benchmark.CAPTURE_LIMIT, len(record["execution"]["stdout"]))
        self.assertIn("capture limit", record["errors"][0])

    def test_artifact_mutation_fails_collection(self):
        (self.root / "evaluator.py").write_text(EVALUATOR + 'Path(os.environ["AIO_BENCHMARK_ARTIFACT"]).write_text("changed")\n')
        self.freeze()
        record = self.collect()
        self.assertIn("artifact changed", record["errors"][0])
        self.assertIsNone(record["result"])

    def test_metrics_reject_booleans_and_nonfinite_numbers(self):
        result = {"gates": {key: True for key in benchmark.GATES}, "metrics": {"value": True}, "notes": []}
        with self.assertRaises(benchmark.BenchmarkError):
            benchmark.validate_evaluation(result, self.definition)
        result["metrics"]["value"] = 10 ** 1000
        with self.assertRaisesRegex(benchmark.BenchmarkError, "finite numbers"):
            benchmark.validate_evaluation(result, self.definition)
        result["metrics"]["value"] = float("inf")
        with self.assertRaises(benchmark.BenchmarkError):
            benchmark.validate_evaluation(result, self.definition)

    def test_comparison_requires_every_pair_and_rejects_duplicates(self):
        self.freeze()
        self.collect()
        with self.assertRaisesRegex(benchmark.BenchmarkError, "every declared"):
            benchmark.compare(self.frozen, self.root, [self.root / "aio.json"], self.root / "comparison.json")
        with self.assertRaisesRegex(benchmark.BenchmarkError, "unique"):
            benchmark.compare(self.frozen, self.root, [self.root / "aio.json"] * 2, self.root / "comparison.json")

    def test_comparison_excludes_metrics_after_a_failed_gate(self):
        self.freeze()
        for condition in self.definition["conditions"]:
            self.collect(condition)
        path = self.root / "superpowers.json"
        record = benchmark.read_json(path)
        record["result"]["gates"]["recovery"] = False
        path.write_text(json.dumps(record))
        report = benchmark.compare(self.frozen, self.root, [self.root / (item + ".json") for item in self.definition["conditions"]], self.root / "comparison.json")
        self.assertTrue(report["conditions"][0]["eligible_for_metrics"])
        self.assertEqual([4], report["conditions"][0]["metrics"]["value"]["values"])
        self.assertFalse(report["conditions"][2]["eligible_for_metrics"])
        self.assertEqual({}, report["conditions"][2]["metrics"])

    def test_comparison_rejects_foreign_protocol(self):
        self.freeze()
        self.collect()
        path = self.root / "aio.json"
        record = benchmark.read_json(path)
        record["definition_sha256"] = "0" * 64
        path.write_text(json.dumps(record))
        with self.assertRaisesRegex(benchmark.BenchmarkError, "share the frozen"):
            benchmark.compare(self.frozen, self.root, [path], self.root / "comparison.json")

    def test_test_report_collection_preserves_failed_scores(self):
        self.definition.update(score_format="test-report", gate_categories={key: [key] for key in benchmark.GATES}, metrics=[{"id": "passed_tests", "direction": "higher"}])
        raw = {"total": 3, "passed": 2, "failed": 1, "errors": [], "categories": {},
               "tests": [{"id": key, "category": key, "status": "failed" if key == "recovery" else "passed"} for key in sorted(benchmark.GATES)]}
        (self.root / "evaluator.py").write_text("print(" + repr(json.dumps(raw)) + ")\nraise SystemExit(1)\n")
        self.freeze()
        record = self.collect()
        self.assertEqual(2, record["result"]["metrics"]["passed_tests"])
        self.assertFalse(record["result"]["gates"]["recovery"])
        self.assertIn("exited 1", record["errors"][0])

    def test_test_report_counts_and_gate_categories_are_fixed(self):
        definition = copy.deepcopy(self.definition)
        definition.update(score_format="test-report", gate_categories={key: [key] for key in benchmark.GATES}, metrics=[{"id": "passed_tests", "direction": "higher"}])
        benchmark.validate_definition(definition)
        raw = {"total": 3, "passed": 2, "failed": 1, "errors": [], "categories": {},
               "tests": [{"id": key, "category": key, "status": "failed" if key == "recovery" else "passed"} for key in sorted(benchmark.GATES)]}
        result = benchmark.normalize_evaluation(raw, definition)
        self.assertEqual(2, result["metrics"]["passed_tests"])
        self.assertFalse(result["gates"]["recovery"])
        self.assertTrue(result["gates"]["security"])
        raw["passed"] = 3
        with self.assertRaisesRegex(benchmark.BenchmarkError, "totals"):
            benchmark.normalize_evaluation(raw, definition)

    def test_test_report_missing_gate_coverage_does_not_pass(self):
        definition = copy.deepcopy(self.definition)
        definition.update(score_format="test-report", gate_categories={key: [key] for key in benchmark.GATES}, metrics=[{"id": "pass_rate", "direction": "higher"}])
        raw = {"total": 1, "passed": 1, "failed": 0, "errors": [], "categories": {}, "tests": [{"id": "one", "status": "passed", "category": "correctness"}]}
        result = benchmark.normalize_evaluation(raw, definition)
        self.assertFalse(result["gates"]["security"])
        self.assertFalse(result["gates"]["recovery"])

    def test_cli_separator_supplies_explicit_argv(self):
        self.freeze()
        output = self.root / "cli.json"
        result = subprocess.run([sys.executable, str(SCRIPT), "collect", str(self.frozen), "--root", str(self.root), "--condition", "aio", "--trial", "trial-1", "--artifact", "artifact.json", "--output", str(output), "--", sys.executable, str(self.root / "evaluator.py")], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(4, benchmark.read_json(output)["result"]["metrics"]["value"])


if __name__ == "__main__":
    unittest.main()
