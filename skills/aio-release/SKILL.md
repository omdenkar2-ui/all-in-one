---
name: aio-release
description: "Prepare and verify backend rollout, compatibility, canary signals and recovery before authorized deployment."
---

# AIO Release

Prepare and verify backend rollout, compatibility, canary signals and recovery before authorized deployment.

## Protocol

1. Establish the actual environment/revision, authorized destination, acceptance, schema compatibility and release owner. Prepare the artifact, migration plan and rollback/reconciliation before any required external approval.
2. Check current-head build/tests/review and operational preconditions. Define canary traffic, thresholds, observation window and rollback triggers from actual service targets.
3. Deploy only when authorized for that environment. Verify deployed revision, health and a real bounded backend request/job; a successful deploy command is not proof of correct service behavior.
4. Observe error/latency/resource/queue indicators and compatibility, using [aio-observe](../aio-observe/SKILL.md) for instrumentation and [aio-canary](../aio-canary/SKILL.md) for a bounded deployment observation. Reuse matching current-release evidence. Trigger authorized rollback/reconciliation when thresholds fail.
5. Return observed release/recovery evidence and remaining risks. Missing access or required signals leaves the release pending; do not publish merely because a pipeline is autonomous.

## Return and handoff

A release dossier and observed authorized rollout/recovery status, separate from local implementation.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
