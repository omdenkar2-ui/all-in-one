---
name: aio-doc-review
description: "Review backend plans, API contracts and runbooks for contradictions, gaps and stale operational claims."
---

# AIO Doc Review

Review backend plans, API contracts and runbooks for contradictions, gaps and stale operational claims.

## Protocol

1. Read the exact document, its authority/source, intended consumers and referenced code/evidence. Separate acceptance facts, design decisions and speculative recommendations.
2. Check interface/state semantics, R/U/V coverage, source freshness, authorization, recovery/versioning and operational instructions against actual implementation or accepted design.
3. Find concrete contradictions and missing decisions that affect execution. Prefer a precise correction over adding broad boilerplate or unsupported guarantees.
4. Return actionable finding IDs, location/consequence and suggested edit. Apply document edits when authorized; document review does not substitute for runtime/code review.

## Return and handoff

A document review or corrected artifact with resolved and outstanding material findings.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
