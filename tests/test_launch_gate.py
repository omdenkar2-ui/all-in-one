"""Exercise mobile gate failure modes with synthetic, explicitly local evidence."""

from copy import deepcopy
from datetime import date
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


PACKAGE = Path(__file__).resolve().parents[1]
SCRIPT = PACKAGE / 'skills/launch-readiness/scripts/launch_gate.py'
SPEC = importlib.util.spec_from_file_location('launch_gate', SCRIPT)
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)
DAY = date(2026, 10, 5)
APPLE = ['https://developer.apple.com/app-store/review/guidelines/',
         'https://developer.apple.com/app-store/app-privacy-details/']
GOOGLE = ['https://support.google.com/googleplay/android-developer/answer/10144311?hl=en',
          'https://support.google.com/googleplay/android-developer/answer/10787469?hl=en']
DELETION = 'https://support.google.com/googleplay/android-developer/answer/13327111?hl=en'


class LaunchGateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='All in One launch evidence ')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'contract.md').write_text('Synthetic acceptance contract.', encoding='utf-8')
        (self.root / 'evidence.txt').write_text('Synthetic fixture, not an actual mobile audit.', encoding='utf-8')
        (self.root / 'ios.ipa').write_bytes(b'fixture iOS artifact, not executable')
        (self.root / 'android.aab').write_bytes(b'fixture Android artifact, not executable')
        self.report = self.make_report(['ios', 'android'])

    def digest(self, name):
        return hashlib.sha256((self.root / name).read_bytes()).hexdigest()

    def make_report(self, platforms, enabled=()):
        features = {key: key in enabled for key in GATE.FEATURES}
        sources = (APPLE if 'ios' in platforms else []) + (GOOGLE if 'android' in platforms else [])
        if 'android' in platforms and features['accounts']:
            sources = sources + [DELETION]
        return {
            'schema_version': 1, 'verdict': 'ready_for_submission',
            'source': {'path': 'contract.md', 'sha256': self.digest('contract.md')},
            'app': {'name': 'Fixture App', 'developer_entity': 'Fixture Developer',
                    'platforms': platforms, 'markets': ['US'], 'features': features},
            'policy_review': {'checked_on': DAY.isoformat(), 'sources': sources, 'evidence': ['evidence.txt']},
            'builds': [{'platform': p, 'path': p + ('.ipa' if p == 'ios' else '.aab'),
                        'sha256': self.digest(p + ('.ipa' if p == 'ios' else '.aab'))} for p in platforms],
            'checks': [{'id': identifier, 'status': 'pass', 'evidence': ['evidence.txt']}
                       for identifier in sorted(GATE.required_checks(platforms, features))],
            'blockers': [],
        }

    def errors(self, report=None):
        return GATE.validate(self.report if report is None else report, self.root, DAY)[0]

    def run_cli(self, report=None, script=SCRIPT, expected=0, extra=()):
        file = self.root / 'report.json'
        file.write_text(json.dumps(self.report if report is None else report), encoding='utf-8')
        result = subprocess.run([sys.executable, '-I', '-S', '-X', 'utf8', str(script), str(file),
                                 '--root', str(self.root), '--as-of', DAY.isoformat(), '--json', *extra],
                                cwd=self.root, capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_valid_single_and_both_platform_evidence(self):
        for platforms in (['ios'], ['android'], ['ios', 'android']):
            with self.subTest(platforms=platforms):
                report = self.make_report(platforms)
                self.assertEqual([], self.errors(report))
                self.assertTrue(self.run_cli(report)['valid'])

    def test_every_enabled_feature_adds_coverage(self):
        report = self.make_report(['ios', 'android'], tuple(GATE.FEATURES))
        self.assertEqual([], self.errors(report))
        for identifier in (*GATE.FEATURES.values(), 'ios-account-deletion', 'android-web-deletion'):
            with self.subTest(check=identifier):
                incomplete = deepcopy(report)
                incomplete['checks'] = [item for item in incomplete['checks'] if item['id'] != identifier]
                self.assertTrue(any(identifier in error for error in self.errors(incomplete)))

    def test_unknown_feature_cannot_establish_readiness(self):
        for value in (None, 'false', 0, [], {}):
            with self.subTest(value=value):
                report = deepcopy(self.report)
                report['app']['features']['tracking'] = value
                self.assertTrue(self.errors(report))

    def test_required_privacy_check_cannot_be_waived(self):
        for status in ('fail', 'unverified', 'not_applicable'):
            with self.subTest(status=status):
                report = deepcopy(self.report)
                item = next(item for item in report['checks'] if item['id'] == 'privacy-policy')
                item.update(status=status, evidence=[], reason='Unavailable fixture evidence')
                self.assertTrue(any('privacy-policy' in error for error in self.errors(report)))

    def test_nonapplicable_optional_feature_requires_reason(self):
        self.report['checks'].append({'id': 'tracking', 'status': 'not_applicable',
                                     'evidence': [], 'reason': 'No tracking in this fixture'})
        self.assertEqual([], self.errors())
        self.report['checks'][-1].pop('reason')
        self.assertTrue(self.errors())

    def test_failed_additional_check_also_blocks(self):
        self.report['checks'].append({'id': 'extra-security', 'status': 'fail',
                                     'evidence': [], 'reason': 'Observed failure'})
        self.assertTrue(self.errors())

    def test_policy_review_must_be_current_actual_day(self):
        for value in ('2026-10-04', '2026-10-06', '', None):
            with self.subTest(day=value):
                self.report['policy_review']['checked_on'] = value
                self.assertTrue(self.errors())

    def test_official_policy_sources_and_policy_evidence_are_required(self):
        for url in APPLE + GOOGLE:
            report = deepcopy(self.report)
            report['policy_review']['sources'].remove(url)
            self.assertTrue(any('official policy' in error for error in self.errors(report)))
        self.report['policy_review']['evidence'] = []
        self.assertTrue(self.errors())

    def test_account_creation_requires_android_deletion_source(self):
        report = self.make_report(['android'], ['accounts'])
        report['policy_review']['sources'].remove(DELETION)
        self.assertTrue(any('13327111' in error for error in self.errors(report)))

    def test_source_and_release_hashes_detect_changed_files(self):
        for file in ('contract.md', 'ios.ipa', 'android.aab'):
            with self.subTest(file=file):
                original = (self.root / file).read_bytes()
                (self.root / file).write_bytes(original + b' changed')
                self.assertTrue(any('differs' in error for error in self.errors()))
                (self.root / file).write_bytes(original)

    def test_missing_platform_build_and_wrong_artifact_extension_block(self):
        self.report['builds'].pop()
        self.assertTrue(any('Missing candidate' in error for error in self.errors()))
        self.report = self.make_report(['android'])
        self.report['builds'][0].update(path='evidence.txt', sha256=self.digest('evidence.txt'))
        self.assertTrue(any('release artifact' in error for error in self.errors()))

    def test_duplicate_checks_and_platforms_block(self):
        for field in ('checks', 'builds'):
            report = deepcopy(self.report)
            report[field].append(deepcopy(report[field][0]))
            self.assertTrue(any('duplicate' in error.lower() for error in self.errors(report)))
        self.report['app']['platforms'].append('ios')
        self.assertTrue(self.errors())

    def test_missing_evidence_and_escaping_paths_block(self):
        for file in ('missing.txt', '../evidence.txt', '/evidence.txt', 'C:/secret.txt', '..\\secret.txt'):
            with self.subTest(path=file):
                report = deepcopy(self.report)
                report['checks'][0]['evidence'] = [file]
                self.assertTrue(self.errors(report))

    def test_blockers_and_nonready_verdicts_cannot_pass(self):
        for verdict in ('blocked', 'review_needed'):
            report = deepcopy(self.report)
            report['verdict'] = verdict
            self.assertFalse(self.run_cli(report, expected=1)['valid'])
        self.report['blockers'] = ['Missing developer declaration']
        self.assertTrue(self.errors())

    def test_recorded_commands_never_execute_and_failed_exit_cannot_pass(self):
        self.report['checks'][0].update(command='create a file named should-not-exist', exit_code=0)
        self.assertTrue(self.run_cli()['valid'])
        self.assertFalse((self.root / 'should-not-exist').exists())
        for exit_code in (1, True, None, '0'):
            self.report['checks'][0]['exit_code'] = exit_code
            self.assertTrue(self.errors())

    def test_malformed_values_produce_errors_without_crashes(self):
        mutations = [('app', []), ('checks', {}), ('builds', [None]), ('policy_review', None),
                     ('source', []), ('blockers', {}), ('schema_version', True)]
        for field, value in mutations:
            with self.subTest(field=field):
                report = deepcopy(self.report)
                report[field] = value
                self.assertTrue(self.errors(report))
        for field in ('platforms', 'markets', 'features'):
            report = deepcopy(self.report)
            report['app'][field] = [None, {}]
            self.assertTrue(self.errors(report))
        self.report['builds'][0]['platform'] = {}
        self.assertTrue(self.errors())

    def test_duplicate_json_keys_rejected_by_cli(self):
        file = self.root / 'duplicate.json'
        file.write_text('{"verdict":"blocked","verdict":"ready_for_submission"}', encoding='utf-8')
        result = subprocess.run([sys.executable, str(SCRIPT), str(file), '--root', str(self.root), '--json'],
                                capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertEqual(1, result.returncode)
        self.assertIn('duplicate JSON key', result.stdout)

    def test_gate_is_read_only(self):
        before = {file.name: file.read_bytes() for file in self.root.iterdir()}
        self.assertEqual([], self.errors())
        self.assertEqual(before, {file.name: file.read_bytes() for file in self.root.iterdir()})

    def test_relocated_gate_keeps_bundled_core_dependency(self):
        installed = self.root / 'plugin with spaces'
        shutil.copytree(PACKAGE / 'skills', installed / 'skills',
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        result = self.run_cli(script=installed / 'skills/launch-readiness/scripts/launch_gate.py')
        self.assertTrue(result['valid'])
        self.assertIn('does not run tests', result['scope'])

    def test_requirements_are_a_listing_not_readiness(self):
        self.report['verdict'] = 'blocked'
        result = self.run_cli(extra=['--requirements'])
        self.assertIn('privacy-policy', result['required_checks'])
        self.assertNotIn('valid', result)
        self.assertIn('no readiness claim', result['scope'])


if __name__ == '__main__':
    unittest.main()
