"""Real checker executions exercise bounds and evidence, not matching script text."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/aio-verify/scripts/run_checks.py'
spec = importlib.util.spec_from_file_location('run_checks', SCRIPT)
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


class CheckRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='aio check runner ')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()

    def check(self, name, code, **options):
        return {'id': name, 'argv': [sys.executable, '-B', '-X', 'utf8', '-c', code], 'cwd': '.', **options}

    def run_checks(self, checks, limits=None, output='evidence', **options):
        config = {'schema_version': 1, 'checks': checks}
        if limits is not None:
            config['limits'] = limits
        config.update(options)
        path = self.root / 'checks.json'
        path.write_text(json.dumps(config), encoding='utf-8')
        result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(SCRIPT),
                                 'checks.json', '--root', str(self.root), '--output-dir', output],
                                capture_output=True, text=True, encoding='utf-8', timeout=12)
        self.assertEqual('', result.stderr)
        return result, json.loads(result.stdout)

    def evidence(self, concise):
        return json.loads((self.root / concise['summary_path']).read_text(encoding='utf-8'))

    def log(self, check, stream):
        return (self.root / check['logs'][stream]['path']).read_bytes()

    def test_portable_alias_and_stream_paths_are_rejected(self):
        for value in ('.git./logs', '.git /logs', 'evidence./logs', 'evidence /logs', 'logs/result.json:extra'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                R.relative_path(self.root, value)
        self.assertEqual(self.root, R.relative_path(self.root, '.'))
        self.assertEqual(self.root / 'normal.json', R.relative_path(self.root, 'normal.json'))

    @unittest.skipUnless(os.name == 'nt', 'physical Win32 alias behavior')
    def test_win32_git_alias_cannot_accept_config_or_write_evidence(self):
        repository_metadata = self.root / '.git'
        repository_metadata.mkdir()
        for role in ('config', 'output', 'cwd', 'requires'):
            with self.subTest(role=role):
                check = self.check('guard', 'print("ran")')
                if role == 'cwd':
                    check['cwd'] = '.git.'
                if role == 'requires':
                    check['requires'] = ['.git./checks.json']
                config = {'schema_version': 1, 'checks': [check]}
                (self.root / 'checks.json').write_text(json.dumps(config), encoding='utf-8')
                (repository_metadata / 'checks.json').write_text(json.dumps(config), encoding='utf-8')
                result = subprocess.run([sys.executable, '-B', str(SCRIPT),
                    '.git./checks.json' if role == 'config' else 'checks.json',
                    '--root', str(self.root), '--output-dir',
                    '.git./alias-evidence' if role == 'output' else 'guard-' + role],
                    capture_output=True, text=True, encoding='utf-8', timeout=10)
                self.assertEqual(2, result.returncode, result.stdout + result.stderr)
                self.assertEqual('error', json.loads(result.stdout)['status'])
                self.assertFalse((repository_metadata / 'alias-evidence').exists())
                self.assertFalse((self.root / ('guard-' + role)).exists())

    def test_success_preserves_distinct_streams_actual_status_and_literal_argv(self):
        literal = 'hello; $(whoami) & echo unsafe > injection.txt'
        check = self.check('ok', 'import sys; print(sys.argv[1]); print("diagnostic", file=sys.stderr)')
        check['argv'].append(literal)
        result, concise = self.run_checks([check])
        self.assertEqual(0, result.returncode)
        self.assertEqual('passed', concise['status'])
        observed = self.evidence(concise)['results'][0]
        self.assertEqual(check['argv'], observed['argv'])
        self.assertEqual(0, observed['exit_code'])
        self.assertTrue(observed['capture_complete'])
        self.assertEqual((literal + '\n').encode(), self.log(observed, 'stdout').replace(b'\r\n', b'\n'))
        self.assertEqual(b'diagnostic\n', self.log(observed, 'stderr').replace(b'\r\n', b'\n'))
        self.assertNotIn(literal, result.stdout)
        self.assertFalse((self.root / 'injection.txt').exists())
        if os.name != 'nt':
            output = self.root / 'evidence'
            self.assertEqual(0o700, stat.S_IMODE(output.stat().st_mode))
            self.assertEqual(0o600, stat.S_IMODE((output / '01.stdout.log').stat().st_mode))

    def test_nonzero_127_is_failed_and_later_independent_check_runs(self):
        result, concise = self.run_checks([self.check('bad', 'import sys; print("actual failure"); sys.exit(127)'),
                                           self.check('later', 'print("continued")')])
        self.assertEqual(1, result.returncode)
        first, later = self.evidence(concise)['results']
        self.assertEqual(('failed', 127), (first['status'], first['exit_code']))
        self.assertIn(b'actual failure', self.log(first, 'stdout'))
        self.assertEqual('passed', later['status'])

    def test_timeout_terminates_direct_child_preserves_partial_logs_and_continues(self):
        before = time.monotonic()
        result, concise = self.run_checks([self.check('hang', 'import time; print("before timeout", flush=True); time.sleep(10)', timeout_seconds=0.25),
                                           self.check('later', 'print("continued")')])
        self.assertLess(time.monotonic() - before, 5)
        self.assertEqual(1, result.returncode)
        first, later = self.evidence(concise)['results']
        self.assertEqual('timeout', first['status'])
        self.assertIsNotNone(first['exit_code'])
        self.assertIn(b'before timeout', self.log(first, 'stdout'))
        self.assertEqual('passed', later['status'])
        self.assertIn('descendants may survive', concise['cleanup_scope'])

    def test_log_cap_drains_both_streams_without_turning_truncated_output_into_pass(self):
        code = 'import os; os.write(1, b"x" * 150000); os.write(2, b"y" * 140000)'
        result, concise = self.run_checks([self.check('large', code)], {'max_log_bytes': 512})
        self.assertEqual(1, result.returncode)
        check = self.evidence(concise)['results'][0]
        self.assertEqual(('incomplete_output', 0), (check['status'], check['exit_code']))
        self.assertFalse(check['capture_complete'])
        self.assertEqual(150000, check['logs']['stdout']['bytes_seen'])
        self.assertEqual(140000, check['logs']['stderr']['bytes_seen'])
        for name, byte in [('stdout', b'x'), ('stderr', b'y')]:
            self.assertEqual(byte * 512, self.log(check, name))
            self.assertTrue(check['logs'][name]['truncated'])
            self.assertTrue(check['logs'][name]['eof'])
        self.assertLess(len(result.stdout), 2000)

    def test_failure_remains_nonzero_when_capture_is_truncated(self):
        result, concise = self.run_checks([self.check('bad', 'import os,sys; os.write(1, b"x"*1000); sys.exit(7)')], {'max_log_bytes': 64})
        self.assertEqual(1, result.returncode)
        check = self.evidence(concise)['results'][0]
        self.assertEqual(('failed', 7), (check['status'], check['exit_code']))
        self.assertFalse(check['capture_complete'])
        self.assertTrue(check['logs']['stdout']['truncated'])

    def test_descendant_held_pipes_do_not_stall_or_claim_complete_capture(self):
        code = 'import subprocess,sys; subprocess.Popen([sys.executable,"-c","import os,tempfile,time; os.chdir(tempfile.gettempdir()); time.sleep(1.5)"], stdout=sys.stdout, stderr=sys.stderr); print("direct child done", flush=True)'
        before = time.monotonic()
        result, concise = self.run_checks([self.check('descendant', code), self.check('later', 'print("later ran")')])
        self.assertLess(time.monotonic() - before, 5)
        self.assertEqual(1, result.returncode)
        first, later = self.evidence(concise)['results']
        self.assertEqual(('incomplete_output', 0), (first['status'], first['exit_code']))
        self.assertFalse(first['capture_complete'])
        self.assertEqual('passed', later['status'])

    def test_missing_tool_and_prerequisite_are_not_passes_or_executed(self):
        missing = {'id': 'missing', 'argv': ['aio-no-such-executable-56e54a2'], 'cwd': '.'}
        needed = self.check('prereq', 'from pathlib import Path; Path("should-not-run").touch()', requires=['absent.file'])
        cwd = self.check('cwd', 'print("never")', cwd='missing-directory')
        result, concise = self.run_checks([missing, needed, cwd, self.check('later', 'print("ran")')])
        self.assertEqual(1, result.returncode)
        results = self.evidence(concise)['results']
        self.assertEqual(['missing_tool', 'prerequisite_missing', 'prerequisite_missing', 'passed'], [row['status'] for row in results])
        self.assertTrue(all(row['exit_code'] is None for row in results[:3]))
        self.assertFalse((self.root / 'should-not-run').exists())

    def test_global_time_budget_leaves_later_checks_explicitly_unexecuted(self):
        result, concise = self.run_checks([self.check('hang', 'import time; time.sleep(10)'),
                                           self.check('later', 'from pathlib import Path; Path("later-ran").touch()')],
                                          {'run_timeout_seconds': 0.2})
        self.assertEqual(1, result.returncode)
        results = self.evidence(concise)['results']
        self.assertEqual(['timeout', 'budget_exhausted'], [row['status'] for row in results])
        self.assertIsNone(results[1]['exit_code'])
        self.assertFalse((self.root / 'later-ran').exists())

    def test_existing_output_files_are_never_overwritten_or_reused(self):
        (self.root / 'evidence').mkdir()
        sentinel = self.root / 'evidence' / 'summary.json'
        sentinel.write_text('user work', encoding='utf-8')
        result, concise = self.run_checks([self.check('ok', 'print("unused")')])
        self.assertEqual(2, result.returncode)
        self.assertEqual('error', concise['status'])
        self.assertEqual('user work', sentinel.read_text(encoding='utf-8'))
        self.assertEqual(['summary.json'], [p.name for p in sentinel.parent.iterdir()])

    def test_workspace_path_escape_rejected_for_config_output_cwd_and_prereqs(self):
        for path in ('../outside', '/absolute', 'C:\\outside', '..\\outside'):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    R.relative_path(self.root, path)
        for updates in ({'cwd': '../escape'}, {'requires': ['../escape']}):
            result, concise = self.run_checks([self.check('ok', 'print("unused")', **updates)])
            self.assertEqual(2, result.returncode)
            self.assertEqual('error', concise['status'])
        result, _ = self.run_checks([self.check('ok', 'print("unused")')], output='../escape')
        self.assertEqual(2, result.returncode)
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), '../checks.json', '--root', str(self.root)], capture_output=True, text=True, timeout=5)
        self.assertEqual(2, result.returncode)
        self.assertFalse((self.root / 'evidence').exists())

    def test_symlink_escape_rejected_without_changing_target(self):
        with tempfile.TemporaryDirectory(prefix='aio outside ') as outside:
            try:
                os.symlink(outside, self.root / 'linked', target_is_directory=True)
            except OSError as exc:
                self.skipTest('symlink creation unavailable: ' + str(exc))
            result, _ = self.run_checks([self.check('ok', 'print("unused")')], output='linked/evidence')
            self.assertEqual(2, result.returncode)
            result, _ = self.run_checks([self.check('ok', 'print("unused")', cwd='linked')])
            self.assertEqual(2, result.returncode)
            self.assertFalse(list(Path(outside).iterdir()))

    def test_invalid_or_empty_config_is_never_an_empty_pass(self):
        for checks, options in [([], {}), ([self.check('x', 'pass'), self.check('x', 'pass')], {}),
                                ([self.check('x', 'pass')], {'unexpected': True}),
                                ([self.check('x', 'pass')], {'limits': {'max_log_bytes': True}}),
                                ([self.check('x', 'pass')], {'limits': {'max_log_bytes': None}}),
                                ([self.check('x', 'pass', timeout_seconds=float('nan'))], {})]:
            with self.subTest(checks=checks, options=options):
                result, concise = self.run_checks(checks, **options)
                self.assertEqual(2, result.returncode)
                self.assertEqual('error', concise['status'])
                self.assertFalse((self.root / 'evidence').exists())

    def test_validate_launches_nothing_and_creates_no_evidence(self):
        checks = [self.check('never', 'from pathlib import Path; Path("side-effect").touch()')]
        (self.root / 'checks.json').write_text(json.dumps({'schema_version': 1, 'checks': checks}), encoding='utf-8')
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), 'checks.json', '--root', str(self.root), '--validate'], capture_output=True, text=True, timeout=5)
        self.assertEqual(0, result.returncode)
        self.assertEqual('valid', json.loads(result.stdout)['status'])
        self.assertFalse((self.root / 'side-effect').exists())
        self.assertEqual(['checks.json'], [p.name for p in self.root.iterdir()])

    def test_capture_creation_failure_is_error_and_later_check_still_runs(self):
        checks = [self.check('first', 'from pathlib import Path; Path("first-ran").touch()'), self.check('later', 'print("later")')]
        (self.root / 'checks.json').write_text(json.dumps({'schema_version': 1, 'checks': checks}), encoding='utf-8')
        original = R.exclusive_file
        def fail_first_stdout(path):
            if path.name == '01.stdout.log':
                raise OSError('simulated storage error')
            return original(path)
        stdout = io.StringIO()
        with patch.object(R, 'exclusive_file', side_effect=fail_first_stdout), contextlib.redirect_stdout(stdout):
            code = R.main(['checks.json', '--root', str(self.root), '--output-dir', 'evidence'])
        self.assertEqual(1, code)
        concise = json.loads(stdout.getvalue())
        results = self.evidence(concise)['results']
        self.assertEqual(['capture_error', 'passed'], [row['status'] for row in results])
        self.assertFalse((self.root / 'first-ran').exists())
        self.assertIn('simulated storage error', results[0]['reason'])

    def test_result_metadata_failure_never_passes_and_does_not_block_later_check(self):
        checks = [self.check('first', 'print("ran")'), self.check('later', 'print("later")')]
        (self.root / 'checks.json').write_text(json.dumps({'schema_version': 1, 'checks': checks}), encoding='utf-8')
        original = R.write_json
        def fail_first_result(path, value):
            if path.name == '01.result.json':
                raise OSError('simulated metadata storage error')
            return original(path, value)
        stdout = io.StringIO()
        with patch.object(R, 'write_json', side_effect=fail_first_result), contextlib.redirect_stdout(stdout):
            code = R.main(['checks.json', '--root', str(self.root), '--output-dir', 'evidence'])
        self.assertEqual(1, code)
        results = self.evidence(json.loads(stdout.getvalue()))['results']
        self.assertEqual(['capture_error', 'passed'], [row['status'] for row in results])
        self.assertEqual(0, results[0]['exit_code'])
        self.assertIsNone(results[0]['evidence_path'])
        self.assertIn('simulated metadata storage error', results[0]['evidence_error'])

    def test_short_evidence_writes_are_completed_or_raise(self):
        class ShortWriter:
            def __init__(self):
                self.value = bytearray()
            def write(self, value):
                self.value.extend(value[:2])
                return min(len(value), 2)
        writer = ShortWriter()
        R.write_bytes(writer, b'complete evidence')
        self.assertEqual(b'complete evidence', writer.value)
        with patch.object(writer, 'write', return_value=0), self.assertRaises(OSError):
            R.write_bytes(writer, b'uncaptured')


if __name__ == '__main__':
    unittest.main()
