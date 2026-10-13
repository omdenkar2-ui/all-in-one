---
name: aio-pipelines
description: "Engineer queue jobs, durable workflows, DAGs and backfills with explicit recovery semantics."
---

# AIO Pipelines

Engineer queue jobs, durable workflows, DAGs and backfills with explicit recovery semantics.

## Protocol

1. Read [pipelines](../all-in-one/references/pipelines.md). Choose direct jobs, a durable orchestrator or a batch DAG from scheduling/recovery requirements; preserve a sufficient existing mechanism.
2. Specify task inputs, partition/window identity, output validation, dependency/join behavior, timeout, retry owner and terminal/dead-letter handling. Pass large artifacts by reference and digest.
3. Define idempotency/reconciliation across effect and acknowledgement boundaries. Persist publication atomically where required and handle repeated delivery or interrupted staged output.
4. For durable runs plan replay/version compatibility; for DAGs define event time, watermarks, late/empty partitions, catchup and overlapping backfill writes. Bound fan-out and total retry/concurrency budget.
5. Implement changed behavior through [aio-tdd](../aio-tdd/SKILL.md), including observed failing evidence before the change. Run duplicate, crash/restart, outage, partial publish, overlap, poison-input and cancellation cases appropriate to the contract. Return actual evidence and unverified operational boundaries.

## Return and handoff

A pipeline implementation with delivery, partition, retry/recovery contracts and tested failure boundaries.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
