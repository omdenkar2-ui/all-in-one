---
name: aio-simplify
description: "Simplify backend changes without weakening contracts, failure behavior or test coverage."
---

# AIO Simplify

Simplify backend changes without weakening contracts, failure behavior or test coverage.

## Protocol

1. Inspect the accepted contract and precise changed scope. Look for needless indirection, duplicated effect/retry logic, speculative extension points and inconsistent error/state handling.
2. Use separate reuse, correctness and complexity passes. Verify an existing abstraction fits before consolidating; similarity of code alone does not mean the contracts are identical.
3. Simplify the smallest owned boundary and preserve authorization, idempotency/recovery, compatibility and resource limits. Avoid an unrelated cleanup that obscures review.
4. Rerun meaningful affected tests and inspect the resulting diff. Record removals and evidence; send unresolved semantic questions to [aio-review](../aio-review/SKILL.md).

## Return and handoff

A simpler verified diff or evidence-backed no-change result, with any deferred complexity explained.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
