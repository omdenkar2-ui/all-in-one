---
name: aio-handoff
description: "Save a concise, source-anchored backend execution handoff that another session can safely resume."
---

# AIO Handoff

Save a concise, source-anchored backend execution handoff that another session can safely resume.

## Protocol

1. Read current files and ledger; record exact repository/branch/revision, accepted plan/source digests, requested destination and settled decisions.
2. List completed/in-progress/blocked U and checkpoint IDs with actual artifacts, commands/results, review findings and external status. Preserve unknowns and user changes.
3. Describe the next concrete action and the evidence needed to accept it, including pending async jobs, credentials/access and unresolved decisions. Do not dump the entire conversation.
4. Write in the project's artifact location and link it. Avoid secrets and machine-only paths inside portable artifacts; use absolute clickable paths only in the user handoff.

## Return and handoff

A durable handoff packet, truthful current state and next action; no fabricated completion or automatic message to another chat.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
