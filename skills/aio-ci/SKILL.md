---
name: aio-ci
description: "Follow required backend PR or build checks to an observed terminal result without inventing CI success."
---

# AIO Ci

Follow required backend PR or build checks to an observed terminal result without inventing CI success.

## Protocol

1. Identify the exact PR/build, current head SHA, repository-required check set and access. Use the installed provider tooling and inspect live status; verify changing APIs in official documentation.
2. Distinguish queued/running, passed, failed, cancelled, skipped and missing required checks. An aggregate green badge or check for an older head is insufficient. An empty/error/auth-failed response is unknown, not a passed empty set. If the project has no applicable CI, return not applicable with actual policy evidence.
3. Use bounded event waits/polls with backoff. Inspect failed job logs and separate product failures from infrastructure/access issues; repair code only when that action is authorized.
4. After a new commit, resume against its head and rerun affected required checks. Do not launch duplicate workflows or cancel another owner's run casually.
5. Return passed only when every required current-head check has an observed acceptable conclusion. A skip is acceptable only when the actual host/project policy and recorded reason permit it; otherwise it stays unresolved. Preserve the real skipped status in the evidence. Timeout, unavailable access or pending checks remain pending/attention with the next action.

## Return and handoff

A current-head CI receipt with required checks, URLs/results, pending/failure reasons and next action.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
