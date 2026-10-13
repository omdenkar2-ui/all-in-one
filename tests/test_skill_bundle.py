"""Check installable specialist resources, provenance and vendored CLI compatibility."""

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urlsplit


PACKAGE = Path(__file__).resolve().parents[1]
SKILLS = PACKAGE / 'skills'
LEGACY = {'all-in-one', 'complete-destruction', 'backend-plan', 'agent-workflows',
            'backend-pipelines', 'backend-algorithms', 'backend-debug', 'backend-review',
            'backend-verify', 'launch-readiness', 'apple-appstore-reviewer', 'play-policy-insights'}
VENDORED = {'apple-appstore-reviewer', 'play-policy-insights'}
CATALOG = json.loads((PACKAGE / 'skill-catalog.json').read_text(encoding='utf-8'))
AIO = {record['name'] for record in CATALOG['specialists']}
ANALYSIS = set(CATALOG.get('optional_analysis', []))
EXPECTED = LEGACY | AIO | ANALYSIS


class SkillBundleTests(unittest.TestCase):
    def run_script(self, script, *arguments, cwd, expected=0):
        result = subprocess.run([sys.executable, '-X', 'utf8', str(script), *map(str, arguments)],
                                cwd=cwd, capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
        return result

    def test_full_catalog_has_distinct_installable_skills_with_ui_metadata(self):
        actual = {path.parent.name for path in SKILLS.glob('*/SKILL.md')}
        self.assertEqual(EXPECTED, actual)
        self.assertEqual(42, len(AIO))
        self.assertEqual({'reverse-engineer-anything'}, ANALYSIS)
        self.assertEqual(55, len(actual))
        self.assertEqual(len(AIO), len(CATALOG['specialists']))
        self.assertEqual('backend', CATALOG['scope'])
        self.assertTrue({'aio-work','aio-plan','aio-review','aio-verify','aio-architecture',
                         'aio-tdd','aio-ci','aio-ship','aio-resume','aio-benchmark',
                         'aio-test-audit','aio-devex-review','aio-canary',
                         'aio-autoplan','aio-qa','aio-qa-only'} <= AIO)
        self.assertEqual({'all-in-one','complete-destruction'}, set(CATALOG['controllers']))
        self.assertEqual(LEGACY - set(CATALOG['controllers']) - set(CATALOG['optional_launch']),
                         set(CATALOG['compatibility_aliases']))
        self.assertTrue(set(CATALOG['compatibility_aliases'].values()) <= AIO)
        self.assertEqual(CATALOG['version'], json.loads((PACKAGE / '.codex-plugin/plugin.json').read_text())['version'])
        for name in actual:
            with self.subTest(skill=name):
                text = (SKILLS / name / 'SKILL.md').read_text(encoding='utf-8')
                self.assertRegex(text, '^---\nname: ' + re.escape(name) + '\n')
                if name not in VENDORED:
                    ui = (SKILLS / name / 'agents/openai.yaml').read_text(encoding='utf-8')
                    self.assertIn('$' + name, ui)
                    self.assertIn('allow_implicit_invocation: true', ui)

    def test_local_links_in_original_skills_and_references_resolve_inside_plugin(self):
        files = []
        for name in EXPECTED - VENDORED - ANALYSIS:
            files.extend((SKILLS / name).rglob('*.md'))
        for path in files:
            text = path.read_text(encoding='utf-8')
            for relative in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
                if urlsplit(relative).scheme or relative.startswith('#'):
                    continue
                with self.subTest(file=path.relative_to(PACKAGE).as_posix(), link=relative):
                    target = (path.parent / relative.split('#', 1)[0]).resolve()
                    self.assertTrue(target.is_relative_to(PACKAGE.resolve()))
                    self.assertTrue(target.is_file())

    def test_vendored_resources_match_pinned_source_hashes_and_keep_licenses(self):
        document = json.loads((SKILLS / 'launch-readiness/references/vendored-sources.json').read_text(encoding='utf-8'))
        self.assertEqual(VENDORED, {source['skill'] for source in document['sources']})
        for source in document['sources']:
            self.assertTrue(source['copied_without_modification'])
            self.assertRegex(source['commit_sha'], r'^[a-f0-9]{40}$')
            for item in source['files']:
                with self.subTest(skill=source['skill'], file=item['path']):
                    path = (SKILLS / source['skill'] / item['path']).resolve()
                    self.assertTrue(path.is_relative_to((SKILLS / source['skill']).resolve()))
                    self.assertEqual(item['sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
                    self.assertIn(source['commit_sha'], item['url'])
                    self.assertEqual('https', urlsplit(item['url']).scheme)
            self.assertTrue(any(item['path'].startswith('LICENSE') for item in source['files']))
            actual = {path.relative_to(SKILLS / source['skill']).as_posix()
                      for path in (SKILLS / source['skill']).rglob('*')
                      if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc'}
            self.assertEqual({item['path'] for item in source['files']}, actual)

    def test_vendored_google_cli_initializes_aggregates_and_renders_fixture(self):
        # This is a CLI/resources smoke test, not a worker audit or real store verdict.
        script = SKILLS / 'play-policy-insights/scripts/orchestrator.py'
        with tempfile.TemporaryDirectory(prefix='All in One Android fixture ') as temporary:
            root = Path(temporary)
            app = root / 'fixture-app'
            manifest = app / 'app/src/main/AndroidManifest.xml'
            manifest.parent.mkdir(parents=True)
            manifest.write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android" '
                                'package="dev.aione.fixture"><uses-permission android:name="android.permission.INTERNET"/>'
                                '<application android:label="Fixture"/></manifest>', encoding='utf-8')
            (app / 'app/build.gradle.kts').write_text('plugins { id("com.android.application") }\n'
                                                     'android { namespace = "dev.aione.fixture"\n'
                                                     'defaultConfig { applicationId = "dev.aione.fixture"\n'
                                                     'targetSdk = 36 } }', encoding='utf-8')
            info = app / 'play_store_assets/play_store_info.json'
            info.parent.mkdir()
            info.write_text(json.dumps({'is_published': False, 'package_name': 'dev.aione.fixture',
                                        'fixture_only': True}), encoding='utf-8')
            initialized = json.loads(self.run_script(script, 'init', app, cwd=root).stdout)
            scratch = Path(initialized['temp_dir']).resolve()
            self.assertTrue(scratch.is_relative_to((root / '.scratch').resolve()))
            self.assertTrue((scratch / 'manifest_details.json').is_file())
            for goal in initialized['activated_goals']:
                self.assertTrue((scratch / f'prompt_worker_{goal}.md').is_file())
                self.assertTrue((scratch / f'input_worker_{goal}.json').is_file())
            # Explicit synthetic input checks aggregation/resource rendering only.
            (scratch / 'worker_fixture.json').write_text(json.dumps({'findings': [{
                'policy_id': 'fixture', 'issue_summary': 'Synthetic fixture for CLI compatibility',
                'severity': 'IMPORTANT', 'files_involved': ['app/src/main/AndroidManifest.xml'],
                'recommendation': 'Synthetic fixture only', 'category': 'Permissions',
                'evidence': 'Fixture, not an actual app finding'}]}), encoding='utf-8')
            aggregated = json.loads(self.run_script(script, 'aggregate', scratch, cwd=root).stdout)
            self.assertGreater(aggregated['critic_chunks'], 0)
            self.assertTrue((scratch / 'prompt_critic_1.md').is_file())
            findings = json.loads((scratch / 'aggregated_findings.json').read_text(encoding='utf-8'))
            self.assertEqual(1, len(findings['findings']))
            self.assertEqual('worker_fixture.json', findings['findings'][0]['worker_file'])
            self.run_script(SKILLS / 'play-policy-insights/scripts/generate_report.py', scratch, cwd=root)
            self.assertTrue((scratch / 'compliance_report.md').is_file())
            self.assertTrue((scratch / 'compliance_report.json').is_file())

    def test_vendored_google_invalid_app_fails_without_a_success_report(self):
        with tempfile.TemporaryDirectory(prefix='All in One invalid Android ') as temporary:
            root = Path(temporary)
            self.run_script(SKILLS / 'play-policy-insights/scripts/orchestrator.py',
                            'init', root / 'missing-app', cwd=root, expected=1)
            self.assertFalse((root / '.scratch').exists())


if __name__ == '__main__':
    unittest.main()
