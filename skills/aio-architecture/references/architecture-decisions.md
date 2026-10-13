# Architecture decisions for agent and workflow backends

## Execution model

| Model | Fits | Consequence to justify |
| --- | --- | --- |
| Synchronous service | Bounded work within a request deadline | Caller retry and timeout-after-write behavior |
| Queue and worker | Independent background unit | Delivery semantics, deduplication, lease and terminal status |
| Explicit agent state machine | Model/tool decisions over evolving state | Typed transitions, tool authority, state persistence and budget limits |
| Durable coordinator | Long waits or several recoverable external steps | Replay-safe orchestration, activities, versioned history and reconciliation |
| Partitioned DAG | Scheduled data with dependency/backfill requirements | Partition identity, watermark, rerun effects and partial completion |

These are architectural choices, not preferred products. Reuse the project's implementation where it meets the contract. Splitting services needs an ownership, deployment, isolation or scale reason.

## State and identities

Define a versioned state schema and legal transitions. Specify whether each field is immutable, last-write-wins, append-only or merged by a reducer; decide how repeated and concurrent updates behave. Restrict writes to the component that owns the field. Graph nodes must produce validated typed updates; invalid model output cannot write arbitrary state or select unrestricted tools.

Keep identities distinct: request correlation, logical run, retry attempt, business operation and external provider reference. A new attempt must not create a new business-operation identity when retrying the same effect. Bind operation identity to tenant and normalized business intent so a reused key with different inputs is rejected. Decide who may resume or inspect a run.

## Proposal, authorization and effect boundaries

A model can propose an action. The executor verifies the authenticated principal, tenant, tool capability, schema, remaining budget and any necessary user authorization before executing it. Instructions embedded in retrieved documents or tool output have no authority to expand capabilities. Use constrained tools with domain operations instead of exposing unrestricted SQL or shell by default.

Separate planning state, effect intent, external execution and committed observation. Name the transaction that owns the intent and status update. Persist only what recovery needs; model messages may contain secrets or personal data. Decide redaction, retention, encryption and tenant-scoped access.

## Durability and replay

Specify the acknowledgment point and what is durable at each boundary. Replay must reuse recorded nondeterministic outcomes; put network calls, random choices, clocks and effects behind the chosen runtime's durable activity boundary when its replay contract requires this. Do not claim exactly-once external execution from a local checkpoint.

For a critical external operation, document the crash window explicitly:

1. Intent persisted with operation ID and tenant-scoped authorization.
2. Effect requested using that ID or provider-supported deduplication.
3. Provider may succeed while the worker loses its response.
4. Retry reconciles by the same ID/provider reference; it does not blindly repeat an irreversible effect.
5. Observation is persisted and the run reaches a defined terminal state.

When reconciliation is impossible, specify `needs_attention` or another honest unresolved state with operator evidence. Compensation has its own authorization, identity, failure modes and retry limits; it is not an automatic inverse transaction.

## Concrete trace: case-creation agent

For an agent that drafts and opens a support case, a possible contract is:

```text
RunState = {schema_version, tenant_id, run_id, status,
            operation_id, proposal, effect_reference, budget_remaining}
ToolProposal = {tool: "create_case", arguments: {summary, customer_id}}
CreateCase = (authenticated_tenant, operation_id, validated_arguments)
             -> Created(case_id) | Rejected(code) | Unknown(operation_id)
```

The server binds tenant/run/operation identities; a model cannot replace them. A proposal reducer replaces only the validated draft, while committed effect references are immutable. The executor checks customer ownership and capability before entering `effect_pending`. A second worker must acquire the same operation record rather than open another case concurrently.

Suppose the provider creates a case and the worker crashes before storing its ID. Resume looks up the operation using the same deduplication key or recorded provider correlation reference. A found case leads to `completed` with the same case ID; an explicit rejection leads to `failed`; an unresolvable result leads to `needs_attention`. Repeating the request with a different customer under the same operation key is a conflict. Test these transitions with the interruption placed exactly between provider success and local persistence.

This illustrates a contract rather than prescribing a provider API. Verify that the selected provider actually supports lookup/deduplication before claiming recoverable behavior.

## Resource and error contracts

Declare end-to-end and per-dependency deadlines, concurrency limits, queue depth/age, retry count/backoff ownership, token/tool/cost budgets and retained-state limits. A retry is included in the same total budget. Name the behavior when exhausted: fail, defer or request intervention, with a bounded terminal result. Validate estimates using representative distributions, not only an average happy path.

Errors distinguish invalid input, unauthorized, tenant conflict, transient dependency failure, permanent refusal and unknown external outcome. Specify client-visible status, safe details, retry eligibility and operator action. Propagate cancellation while preserving already committed effects and reconciliation records.

## Compatibility and proof

Record API/event/schema versions, old/new reader and writer compatibility, migration/backfill strategy and rollback limitations. Durable histories may outlive a deployment; explicitly decide how older runs finish after a workflow change. Inspect the actual installed runtime and current official documentation before relying on a framework feature.

Map architectural invariants to tests: reducer repeat/concurrency, duplicate operation, restart at each durable boundary, interrupted external success, invalid/untrusted tool proposal, cross-tenant resume, budget exhaustion, cancellation and deployment compatibility. Load or chaos tests are required only where a stated acceptance target needs them; mark missing environments as unverified.
