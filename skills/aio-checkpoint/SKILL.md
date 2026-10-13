---
name: aio-checkpoint
description: "Reconcile backend plan, units, review and verification evidence before advancing a pipeline stage."
---

# AIO Checkpoint

Reconcile backend plan, units, review and verification evidence before advancing a pipeline stage.

## Protocol

1. Read the exact accepted source, plan and run ledger. Match stable R/U/V IDs, revision/digests and checkpoint prerequisites to actual files/results.
2. Run the plan gate before substantial implementation and the completion receipt checker before full completion. Add the mobile launch gate only when that release is in scope.
3. Inspect semantic coverage and actual observations beyond helper output: expected behavior, current-head tests, independent review and observed delivery. Mechanical validation alone cannot authenticate commands.
4. Advance only the checkpoint whose prerequisites and acceptance are satisfied. Failed, unavailable or stale evidence remains blocked/pending with a recovery action; a retry cap never changes its verdict.

## Return and handoff

An observed stage decision and updated ledger/evidence, separate from a general reliability certification.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
