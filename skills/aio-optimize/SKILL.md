---
name: aio-optimize
description: "Diagnose and improve backend performance using representative profiles and correctness checks."
---

# AIO Optimize

Diagnose and improve backend performance using representative profiles and correctness checks.

## Protocol

1. Read [algorithms](../all-in-one/references/algorithms.md) and establish the metric, workload distribution, baseline environment and acceptance target.
2. Profile the actual hot boundary: CPU, memory, database plans/round trips, serialization, contention, queue latency or external waits. A guessed bottleneck is not a measurement.
3. Make one evidence-backed change, preserving a correctness oracle and relevant failure tests. Bound concurrency/cache/connection changes and inspect cancellation, invalidation and overload effects.
4. Compare repeated baseline/candidate runs under the same workload and environment. Include p50/p95 or tails, throughput/error rate and resource use where those are the acceptance dimensions.
5. Keep, revert or narrow the optimization from measured results and explain tradeoffs. Stop when the target is met; do not sacrifice tenant/security/correctness checks for a benchmark win.

## Return and handoff

A reproducible baseline/candidate report and verified performance change with measured scope.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
