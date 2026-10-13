# Backend architecture

Start with a concrete request path: caller -> authorization -> validation -> service -> transaction or queue -> result. Name who owns each datum and which boundary may fail. Record the volume, payload distribution, latency target, consistency requirement, recovery target, and permitted cost. Unknown values are assumptions to test, not invented service guarantees.

## Choose the smallest viable execution model

| Need | Initial choice | Add complexity when |
| --- | --- | --- |
| Short bounded request | Synchronous handler | Work exceeds response deadline |
| Independent background work | Job queue and worker | Recovery spans several durable steps |
| Model/tool decisions with evolving state | Explicit agent state machine | Branching and checkpoints justify a graph |
| Multi-step durable external operations | Durable orchestrator | Crash recovery and long waits must survive worker loss |
| Scheduled partitioned data processing | Batch tasks or DAG scheduler | Dependencies and backfills need explicit management |

A modular service is a reasonable starting point. Split services when ownership, deployment, isolation, or scale requires it. Do not introduce Temporal, LangGraph, Airflow, or distributed messaging solely because this skill references them.

## Define boundaries before code

Give API requests typed input, authorization context, validation rules, stable error categories, and timeout behavior. Separate domain logic from transport, database, and external clients so correctness tests can exercise the domain without network setup. Specify compatibility for API/schema changes and who consumes each event.

For asynchronous work, define the acknowledgement boundary. A queued acknowledgement means accepted, not completed. Provide a stable job ID, status transitions, terminal errors, and authorized retrieval of the result. Define what happens if the client times out after a write succeeds.

Avoid a database write followed by a best-effort publish when both must happen. Consider a transactional outbox written with domain state, then a retryable publisher with deduplicating consumers. The outbox adds storage and cleanup work; use it only where lost publication violates the contract.

## Bound resource use

Budget total latency across dependencies; propagate cancellation and deadlines. Bound concurrency and queue size, and define overload behavior. Calculate database connections across processes, replicas, workers, and administration. Retry storms must not consume the entire capacity budget.

Carry tenant, request, job, and workflow correlation IDs through traces and structured logs. Log transitions and outcomes without credentials or unrestricted model payloads. Measure queue age, error rate, retry exhaustion, and latency percentiles. Alerts need an owner and a recovery action.

Verify with a representative successful request, malformed/unauthorized inputs, timeout after commit, worker loss, downstream outage, and sustained load where the acceptance contract requires it. Architectural diagrams help only when they expose ownership and failure boundaries.

## Focused execution stages

Use [AIO Plan Review](../../aio-plan-review/SKILL.md) for the failure handling/test/observability ledger on affected backend paths.
