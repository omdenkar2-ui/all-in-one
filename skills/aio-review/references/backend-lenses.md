# Backend review lenses

Read only the rows relevant to the changed mechanism. Review [core security guidance](../../all-in-one/references/security.md), [agent workflows](../../all-in-one/references/agent-workflows.md), [pipelines](../../all-in-one/references/pipelines.md), [data](../../all-in-one/references/data.md), or [algorithms](../../all-in-one/references/algorithms.md) when more domain context is needed.

| Mechanism | Concrete review trace |
| --- | --- |
| API/authentication | Trace validated identity into each read/write, object identifier and tenant predicate. Check absent/expired credentials, cross-tenant IDs, pagination, error leakage, rate/size limits and backwards-compatible error/result shapes. |
| External effects | Follow claim/effect/commit/ack ordering. Ask what happens if the process dies immediately after the provider succeeds, or two workers claim the same key. Check durable idempotency key, uniqueness, provider reconciliation and retries across layers. |
| Durable workflow | Verify replayable state transitions, versioned checkpoint schema, resumption, stale workers, lease expiry, cancellation, bounded retries and exhausted-job handling. Ensure retries do not repeat committed effects. |
| Agent/tool boundary | Trace untrusted model/tool/document output into validated tools and data access. Check permission narrowing, secret handling, tenant memory isolation, confirmation for high-impact effects, budgets, termination and safe recovery after model/provider failure. |
| Migration/data | Inspect old/new reader and writer compatibility, locking/scan cost, transaction boundaries, defaults/backfill, uniqueness under concurrency, rollback/data preservation and schema enforcement in actual database tests. |
| Event/DAG pipeline | Trace duplicate, delayed, out-of-order and poison events; partition/order assumptions; watermark/window boundaries; backfills; partial sink failures; lineage; ack/retry/dead-letter handling and real source/sink behavior. |
| Algorithm/performance | Verify a correctness oracle and edge domain, adversarial inputs, precision/overflow, complexity and memory bounds, stable benchmarking fixtures, cold/warm behavior and equivalent outputs after optimization. |
| Operational release | Compare required CI status to the reviewed head, inspect runtime/config/secrets, health metrics, rollback authority and migration compatibility. A prior green commit does not approve a moved head. |

For concurrency, reason about a specific interleaving rather than saying thread safe. For resource claims, identify the measured or derived bound and workload. For replay claims, name the persisted transition and failure window. For model-quality claims, ask for a fixed versioned evaluation corpus with outcome criteria, baseline, seeds where supported and budget; a single attractive response is insufficient.
