# Plan index schema and structural gate

The complete narrative explains decisions and execution. The JSON index lets the bundled gate reject disconnected coverage, unsafe file ownership, stale sources and unresolved structural blockers. It cannot authenticate a review, run a command or establish that a test proves its assertion.

```text
python "<plugin-dir>/skills/all-in-one/scripts/plan_gate.py" "<plan.json>" --root "<workspace>" --json
```

Use Python 3.10+ and paths resolved from the installed skill, not the caller's current directory. The [starter](../templates/plan.json) is deliberately blocked; filling a status field is not readiness.

## Required fields

| Field | Shape and meaning |
| --- | --- |
| `schema_version` | Integer `1` |
| `status` | `ready` or `blocked`; records structural candidate readiness, not completed semantic review |
| `source` | `{ "path": "contract.md", "sha256": "64 lowercase hex digits" }`; existing workspace-contained canonical source |
| `requirements` | Nonempty list of `{ "id": "R1", "text": "observable requirement" }` |
| `units` | Nonempty list of `{ "id": "U1", "requirement_ids": ["R1"], "depends_on": [], "owner": "integrator", "files": ["src/new_file.py"], "verification_ids": ["V1"] }` |
| `verification` | Nonempty list of `{ "id": "V1", "unit_ids": ["U1"], "command": "exact command", "assertions": ["observable invariant"] }` |
| `binding_decisions` | List of `{ "id": "D1", "status": "resolved", "resolution": "decision and evidence" }`; unresolved decisions require resolution before readiness |
| `blockers` | List of concrete strings; ready plans require an empty list |

IDs are unique in their category. Requirements must have unit coverage; units and verification records link to each other in both directions. Dependencies must reference known units and form an acyclic graph. Every unit has a nonempty single owner and exact file paths. Planned new files are valid; paths must remain inside the workspace, excluding `.git`, drives, wildcards and traversal. Existing parent symlinks must not escape the workspace.

Two units owning the same file require a dependency relationship and a nonempty `ownership_note` on **both** units that explains the sequential edit/handoff. A shared owner name alone does not authorize parallel edits.

## Optional metadata

Top-level `context` and `architecture` are objects, `reviews` is a list of review objects, and `risks` is a list of strings. Use them to point to the narrative and evidence; the gate does not prove their semantic content.

Unit records may add string fields `title`, `test_first` and `ownership_note`, plus string arrays `inputs`, `outputs` and `acceptance`. `test_first` describes the expected failing proof; it is not an execution result. Record precise interfaces, the red/green sequence and acceptance here or in the indexed narrative. Verification records may add strings `cwd` and `phase`, and boolean `failure_expected`. Preserve exact names; unknown fields are rejected to expose typos.

## Readiness remains two checks

1. Populate the current source and JSON index, resolve structural blockers, then mark the candidate index `status: ready` and run the gate. A pass means its structural contract is coherent; it does not mean independent review has completed.
2. Complete AIO Plan Review against the current narrative, source and repository evidence; resolve binding findings, rerun affected structural checks and record the actual review state.

Keep the **stage return and execution ledger** blocked while either required check is incomplete. Use JSON `status: blocked` for unresolved structural prerequisites or binding findings; a structurally ready candidate can await semantic review without falsely claiming execution readiness. Source edits, changed interfaces or new binding findings reopen affected plan decisions. Hand the plan to AIO Work only after both checks are satisfied.
