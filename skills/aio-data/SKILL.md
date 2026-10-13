---
name: aio-data
description: "Plan and implement backend schemas, transactions, tenant access and compatible data migrations."
---

# AIO Data

Plan and implement backend schemas, transactions, tenant access and compatible data migrations.

## Protocol

1. Read [data](../all-in-one/references/data.md), current schema/query plans and the exact access roles. Put invariants in constraints/transactions where appropriate rather than relying only on application checks.
2. Model ownership, uniqueness/idempotency, transactional effect/outbox boundaries and tenant predicates. Test with actual constrained roles; administrator success is not evidence of isolation.
3. Design migrations for mixed old/new code, realistic data volume, locks, backfill restart and validation. Use expand/migrate/contract where compatibility requires it; destructive cleanup needs actual authorization.
4. Use [aio-tdd](../aio-tdd/SKILL.md) for changed invariants and access behavior. Measure affected query plans and connection budgets. Verify concurrent writes, rollback, duplicate identity, stale readers, tenant access, migration interruption and old/new consumers.
5. Record rollout/recovery and retention/deletion implications. A rollback command is insufficient when data loss or irreversible transformation must be addressed separately.

## Return and handoff

A schema/migration/query change with invariant, compatibility, access and operational evidence.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
