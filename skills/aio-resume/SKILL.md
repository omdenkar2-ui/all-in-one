---
name: aio-resume
description: "Resume the exact saved backend run after reconciling its ledger with current source and evidence."
---

# AIO Resume

Resume the exact saved backend run after reconciling its ledger with current source and evidence.

## Protocol

1. Open the user-identified handoff/plan and current repository. Never choose the newest unrelated plan or treat the existence of a plan path as implementation authority.
2. Compare source/revision/digests, units, decisions, working-tree changes and external CI/deploy state with the saved ledger. Identify completed, stale or invalidated evidence.
3. Reconcile drift explicitly: preserve new user work, rerun invalidated checks and revise dependencies/source identity where the accepted scope permits. A conflicting settled decision needs resolution.
4. Return the reconciled next checkpoint to an existing integrating controller. Only a standalone authorized resume restores top-level execution through [aio-work](../aio-work/SKILL.md) or Complete Destruction. Do not replay successful external effects or redo completed units solely because context was lost.

## Return and handoff

A reconciled resume decision, valid source/ledger identity and continued authorized work or a precise blocker.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
