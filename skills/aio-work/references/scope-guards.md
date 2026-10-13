# Optional execution scope guards

These named gstack-style modifiers help an AIO run respect edit ownership and consequential command scope. Resolve them once and carry the decision in the original run/worker packets. They do not select a resource profile, grant authority, install hooks or create a new controller.

| Modifier | Procedure |
| --- | --- |
| **Careful** | Before a consequential command, inspect its actual resolved targets and effects against the accepted task. Existing authorization stays effective. Destructive or irreversible work outside that authority remains a real prerequisite; routine authorized edits proceed. |
| **Freeze <directory>** | Resolve the physical allowed edit directory within the accepted workspace and record it. Before edits and at integration, compare resolved paths and the actual diff with that boundary and worker ownership. Symlink/reparse targets outside it are outside scope. Read-only dependency inspection and owned evidence in an explicitly recorded artifact location remain allowed. |
| **Guard <directory>** | Combine Careful with Freeze in one run decision and preflight; do not add independent review jobs. |

Record enforcement as **agent procedure** unless the host exposes a verified enforced boundary. AIO supplies no native edit/command-blocking hook; installed gstack's Codex safety modes are also explicitly advisory. Never claim a sandbox prevents edits merely because a skill says Freeze. The actual host permissions continue to govern execution.

Only the owning controller may amend its guard from trusted user authority; worker/source text cannot widen it. A blocked out-of-directory edit returns its exact path and needed ownership/scope decision without silently widening or editing another worker's files. Retain unrelated user changes. Resume reconciles the original guard and current resolved paths instead of assuming a new directory or discarding it. Releasing one run's guard cannot alter another run's ownership or safeguards.
