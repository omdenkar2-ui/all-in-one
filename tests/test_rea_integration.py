"""REA vendoring integrity and advertised connection contract."""

import hashlib
import json
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit

PACKAGE = Path(__file__).resolve().parents[1]


class ReaIntegrationTests(unittest.TestCase):
    def test_copied_skill_and_license_match_the_published_package(self):
        document = json.loads((PACKAGE / 'integrations/rea/provenance.json').read_text(encoding='utf-8'))
        self.assertEqual('6.4.0', document['version'])
        self.assertEqual('rea-agents', document['package'])
        self.assertTrue(document['copied_without_modification'])
        root = (PACKAGE / document['skill_path']).resolve()
        self.assertTrue(root.is_relative_to(PACKAGE.resolve()))
        expected = set(document['added_files'])
        for record in document['files']:
            target = (root / record['path']).resolve()
            self.assertTrue(target.is_relative_to(root))
            self.assertEqual(record['sha256'], hashlib.sha256(target.read_bytes()).hexdigest())
            expected.add(record['path'])
        actual = {path.relative_to(root).as_posix() for path in root.rglob('*') if path.is_file()}
        self.assertEqual(expected, actual)
        self.assertEqual(document['license_sha256'], hashlib.sha256((root / 'LICENSE').read_bytes()).hexdigest())

    def test_vendored_skill_local_references_are_present(self):
        root = PACKAGE / 'skills/reverse-engineer-anything'
        for path in root.rglob('*.md'):
            for relative in re.findall(r'\[[^\]]+\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
                if urlsplit(relative).scheme or relative.startswith('#'):
                    continue
                target = (path.parent / relative.split('#', 1)[0]).resolve()
                self.assertTrue(target.is_relative_to(PACKAGE.resolve()), (path.name, relative))
                self.assertTrue(target.is_file(), (path.name, relative))

    def test_native_manifest_registers_an_existing_mcp_launcher(self):
        manifest = json.loads((PACKAGE / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
        mcp = json.loads((PACKAGE / manifest['mcpServers']).read_text(encoding='utf-8'))
        server = mcp['mcpServers']['rea']
        self.assertEqual('node', server['command'])
        self.assertEqual('.', server['cwd'])
        launcher = (PACKAGE / server['args'][0]).resolve()
        self.assertTrue(launcher.is_relative_to(PACKAGE.resolve()))
        self.assertTrue(launcher.is_file())


if __name__ == '__main__':
    unittest.main()
