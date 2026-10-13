"""Independent checks of the shipped package, source trails, and offline relocation."""

import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urlsplit


PACKAGE = Path(__file__).resolve().parents[1]
SKILL = PACKAGE / "skills" / "all-in-one"
DOMAINS = {
    "architecture", "agents", "pipelines", "algorithms", "data",
    "security", "verification", "delivery", "debugging",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class PackageTests(unittest.TestCase):
    def contained_path(self, root, relative):
        self.assertIsInstance(relative, str)
        self.assertFalse(Path(relative).is_absolute(), relative)
        target = (root / relative).resolve()
        self.assertTrue(target.is_relative_to(root.resolve()), relative)
        return target

    def run_tool(self, script, *arguments, cwd, expected=0):
        # Isolated, without site packages or PYTHONPATH; run outside the package.
        environment = dict(os.environ)
        environment.pop("PYTHONHOME", None)
        environment.pop("PYTHONPATH", None)
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-X", "utf8", str(script), *arguments],
            cwd=cwd, env=environment, capture_output=True, text=True,
            encoding="utf-8", timeout=30,
        )
        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
        return result

    def test_native_registration_points_to_the_delivered_skill(self):
        plugin = read_json(PACKAGE / ".codex-plugin" / "plugin.json")
        marketplace = read_json(PACKAGE / ".claude-plugin" / "marketplace.json")
        self.assertEqual("all-in-one", plugin["name"])
        self.assertEqual("All in One", plugin["interface"]["displayName"])
        self.assertRegex(plugin["version"], r"^\d+\.\d+\.\d+$")
        skills = self.contained_path(PACKAGE, plugin["skills"])
        self.assertTrue((skills / plugin["name"] / "SKILL.md").is_file())
        entries = [entry for entry in marketplace["plugins"] if entry["name"] == plugin["name"]]
        self.assertEqual(1, len(entries), "Marketplace must identify one installable All in One package")
        source = self.contained_path(PACKAGE, entries[0]["source"])
        self.assertEqual(PACKAGE.resolve(), source)
        self.assertTrue((source / ".codex-plugin" / "plugin.json").is_file())

    def test_skill_links_and_domain_playbooks_are_self_contained(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: all-in-one\n"))
        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
        self.assertTrue(links, "Entrypoint must link to its supporting files")
        references = set()
        for relative in links:
            with self.subTest(link=relative):
                self.assertFalse(urlsplit(relative).scheme, "Entrypoint supporting files must be local")
                target = (SKILL / relative).resolve()
                self.assertTrue(target.is_relative_to(PACKAGE.resolve()), relative)
                self.assertTrue(target.is_file(), relative)
                if relative.startswith("references/"):
                    references.add(relative)
        self.assertTrue(
            {"references/agent-workflows.md" if domain == "agents"
             else f"references/{domain}.md" for domain in DOMAINS} <= references,
        )
        self.assertTrue((SKILL / "agents" / "openai.yaml").is_file())

    def test_library_covers_backend_domains_with_inspected_source_trails(self):
        patterns = read_json(SKILL / "knowledge" / "backend-knowledge.json")
        source_document = read_json(SKILL / "knowledge" / "sources.json")
        self.assertEqual(1, patterns["schema_version"])
        self.assertEqual(1, source_document["schema_version"])
        sources = {source["id"]: source for source in source_document["sources"]}
        self.assertEqual(len(sources), len(source_document["sources"]), "Duplicate source IDs")
        self.assertTrue({"compound-engineering", "superpowers"} <= sources.keys())
        self.assertEqual(DOMAINS, {pattern["domain"] for pattern in patterns["patterns"]})
        self.assertEqual(
            len(patterns["patterns"]),
            len({pattern["id"] for pattern in patterns["patterns"]}),
            "Duplicate pattern IDs",
        )
        used_sources = set()
        for pattern in patterns["patterns"]:
            with self.subTest(pattern=pattern["id"]):
                self.assertTrue(pattern["approach"].strip())
                self.assertTrue(pattern["failure_modes"])
                self.assertTrue(pattern["verification"])
                self.assertTrue(pattern["source_ids"])
                self.assertTrue(set(pattern["source_ids"]) <= sources.keys())
                used_sources.update(pattern["source_ids"])
                self.assertTrue(self.contained_path(SKILL, pattern["playbook"]).is_file())
        self.assertEqual(set(sources), used_sources, "An advertised source contributes no knowledge records")
        for source in sources.values():
            with self.subTest(source=source["id"]):
                parsed = urlsplit(source["url"])
                self.assertEqual("https", parsed.scheme)
                self.assertTrue(parsed.hostname)
                self.assertTrue(source["license"])
                if "commit_sha" in source:
                    self.assertRegex(source["commit_sha"], r"^[0-9a-f]{40}$")
                    self.assertIn(source["commit_sha"], source["url"])
                    self.assertRegex(source["skill_sha256"], r"^[0-9a-f]{64}$")
                else:
                    self.assertTrue(source["installed_version"])
                    self.assertTrue(source["inspected_files"])
                    for inspected in source["inspected_files"]:
                        self.assertRegex(inspected["sha256"], r"^[0-9a-f]{64}$")

    def test_runtime_scripts_compile_and_import_only_the_standard_library(self):
        scripts = list((SKILL / "scripts").glob("*.py"))
        self.assertTrue(scripts)
        network_modules = ("socket", "http.client", "urllib.request", "urllib3", "requests")
        for script in scripts:
            with self.subTest(script=script.name):
                text = script.read_text(encoding="utf-8")
                tree = ast.parse(text, filename=script.name)
                compile(tree, script.name, "exec")
                for node in ast.walk(tree):
                    names = []
                    if isinstance(node, ast.Import):
                        names = [alias.name for alias in node.names]
                    elif isinstance(node, ast.ImportFrom):
                        self.assertEqual(0, node.level, "Helpers must not depend on another installed plugin")
                        names = [node.module or ""]
                    for name in names:
                        self.assertIn(name.split(".")[0], sys.stdlib_module_names, name)
                        self.assertFalse(
                            any(name == banned or name.startswith(banned + ".") for banned in network_modules),
                            f"Offline helper imports network module {name}",
                        )

    def test_delivered_runtime_and_guidance_have_no_machine_specific_paths(self):
        host_path = re.compile(
            r"(?i)(?<![a-z0-9])[a-z]:[\\/]|(?<![a-z0-9])/(?:Users|home)/|"
            r"\.codex[\\/](?:plugins|skills)[\\/]"
        )
        files = [PACKAGE / "README.md", SKILL / "SKILL.md"]
        files.extend((SKILL / "references").glob("*.md"))
        files.extend((SKILL / "scripts").glob("*.py"))
        files.extend((SKILL / "knowledge").glob("*.json"))
        for path in files:
            with self.subTest(file=path.relative_to(PACKAGE).as_posix()):
                self.assertIsNone(host_path.search(path.read_text(encoding="utf-8")))

    def test_bundled_index_is_current_and_check_does_not_write_it(self):
        database = SKILL / "knowledge" / "backend-knowledge.sqlite"
        before = hashlib.sha256(database.read_bytes()).digest()
        with tempfile.TemporaryDirectory(prefix="All in One caller ") as temporary:
            result = self.run_tool(SKILL / "scripts" / "knowledge.py", "check", cwd=temporary)
            self.assertIn("Validated", result.stdout)
        self.assertEqual(before, hashlib.sha256(database.read_bytes()).digest())

    def test_relocated_package_rebuilds_searches_and_rejects_unfinished_receipt(self):
        with tempfile.TemporaryDirectory(prefix="All in One portable ") as temporary:
            root = Path(temporary)
            package = root / "installed plugin with spaces"
            caller = root / "unrelated caller"
            caller.mkdir()
            shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
            skill = package / "skills" / "all-in-one"
            helper = skill / "scripts" / "knowledge.py"
            # Recreate the database using only the delivered canonical records.
            (skill / "knowledge" / "backend-knowledge.sqlite").unlink()
            self.run_tool(helper, "build", "--force", cwd=caller)
            self.run_tool(helper, "check", cwd=caller)
            for query, domain in (("recovery", None), ("idempotency", None), ("tenant", "security")):
                with self.subTest(query=query):
                    arguments = ["search", query, "--json"]
                    if domain:
                        arguments.extend(["--domain", domain])
                    matches = json.loads(self.run_tool(helper, *arguments, cwd=caller).stdout)
                    self.assertTrue(matches, f"No actionable knowledge for {query}")
                    for match in matches:
                        if domain:
                            self.assertEqual(domain, match["domain"])
                        self.assertTrue(match["verification"])
                        self.assertTrue(self.contained_path(skill, match["playbook"]).is_file())
                        self.assertTrue(match["sources"])
                        for source in match["sources"]:
                            self.assertEqual("https", urlsplit(source["url"]).scheme)
            sources = json.loads(self.run_tool(helper, "sources", "--json", cwd=caller).stdout)
            self.assertTrue(sources)
            starter = skill / "templates" / "evidence-receipt.json"
            self.assertEqual("blocked", read_json(starter)["status"])
            result = self.run_tool(
                skill / "scripts" / "check_receipt.py", str(starter),
                "--root", str(caller), "--json", cwd=caller, expected=1,
            )
            receipt = json.loads(result.stdout)
            self.assertFalse(receipt["valid"], "A portable starter must never claim completed implementation")
            self.assertTrue(receipt["errors"])
            self.assertIn("does not authenticate", receipt["scope"])


if __name__ == "__main__":
    unittest.main()
