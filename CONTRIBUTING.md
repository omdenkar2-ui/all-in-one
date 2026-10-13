# Contributing to All in One

All in One is a backend engineering plugin for Codex. Contributions should make its guidance clearer, its helpers more reliable, or its verification more useful.

## Getting started

Fork the repository, clone your fork, and make a focused branch. Use Python 3.10+ for the helpers and tests. Node.js and npm are needed only for the REA launcher and runtime. The core test suite uses the Python standard library.

From the repository root:

```sh
python -m unittest discover -s tests -v
python skills/all-in-one/scripts/knowledge.py check
node --check scripts/rea-mcp.mjs
```

Tests skip platform-specific cases where a required facility is unavailable. Include the test result and any skips when submitting a change.

## Where things live

| Path | Purpose |
| --- | --- |
| `skills/<name>/SKILL.md` | A skill's entrypoint and workflow |
| `skills/<name>/references/` | Supporting guidance |
| `skills/all-in-one/scripts/` | Evidence, planning, resource and knowledge helpers |
| `skills/all-in-one/knowledge/` | Canonical patterns, source records and SQLite search index |
| `skill-catalog.json` | Complete skill index |
| `.codex-plugin/plugin.json` | Native plugin metadata |
| `.claude-plugin/marketplace.json` | Marketplace registration used by Codex |
| `.mcp.json` and `scripts/rea-mcp.mjs` | REA tool registration and launcher |
| `tests/` | Package, helper and provenance checks |

Keep links relative and usable after the package moves. Do not add personal paths, credentials, private project material or generated run logs. Preserve the host's instructions and the user's authorization. Keep claims proportional to the evidence the tools actually check.

If canonical knowledge records change, rebuild the index and check it:

```sh
python skills/all-in-one/scripts/knowledge.py build --force
python skills/all-in-one/scripts/knowledge.py check
```

If skills are added or renamed, update the catalog, router links, documentation and relevant package checks together. Coordinate release versions across the plugin manifest, marketplace and catalog.

## Upstream code and licensing

Original contributions use the root MIT license. Bundled third-party files retain their upstream licenses. Read `THIRD_PARTY_NOTICES.md` before modifying those files. Update source provenance and hashes when deliberately updating a vendored dependency; never change recorded hashes merely to silence a failing integrity check. Exact bytes are preserved by `.gitattributes` because provenance tests verify them.

## Pull requests and issues

Explain the problem, the resulting behavior, and how you verified it. For helper behavior changes, include a focused regression test when practical. For documentation-only changes, check links and examples. Report bugs with a minimal reproduction, expected and actual results, plugin/Python versions, and operating system. Remove secrets from examples and logs.

Public GitHub issues are suitable for ordinary bugs. Follow `SECURITY.md` for sensitive reports.
