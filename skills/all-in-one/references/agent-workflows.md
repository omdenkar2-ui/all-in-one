# AI agent workflows

Describe an agent as state, permitted actions, transition rules, and a termination condition. Separate the model's proposal from the application's authorization and execution. Use a simple loop or state machine when that is sufficient.

## State and graph contracts

Define typed durable state: tenant, run ID, current step, inputs/artifact references, decisions, side-effect receipts, error state, and budget consumption. Keep transient network clients and secrets outside serialized state. Specify whether a node returns a partial update or replaces a value.

When branches write the same field, choose an explicit reducer and test its merge behavior. Append-only logs may need stable event IDs to avoid duplication on replay. Reducers must match the scheduler's concurrency semantics; do not assume execution order.

In LangGraph, a `Command(goto=...)` does not automatically suppress an existing static outgoing edge. An unintended static edge can cause both routes to execute. Test graph transitions, fan-out/fan-in, terminal nodes, and unexpected model output against the installed library version.

## Tools and model calls

Give each tool a narrow input/output schema, authorization checks, timeout, and classified failures. Validate model-produced arguments before executing them. Derive tenant and permissions from authenticated context, not model text or a caller-supplied checkpoint ID. Treat retrieved content as untrusted data; it cannot expand tool authority.

Put nondeterministic model calls and external effects outside a durable deterministic workflow's replayed logic. In Temporal, use activities for these operations. Persist decisions/results that must survive restart, and keep activity inputs stable. Avoid logging prompts containing secrets or personal data.

Bound total model calls, tokens/cost, wall time, tool invocations, concurrency, and repair attempts. Retries should have one owner per operation. Classify validation/permanent failures separately from transient rate limits. Add jitter and deadline-aware backoff; circuit breakers do not replace a terminal failure policy.

## Recovery and side effects

Checkpoint state with a stable run identity and select storage suitable for actual restart requirements. A thread/checkpoint identifier selects history; it does not authorize access. Separate checkpoint state from cross-run memory and define retention/deletion for each.

A crash can occur after an external charge succeeds but before its receipt is saved. Use a stable operation ID and the provider's idempotency mechanism where supported; record or reconcile the result before retrying. Never promise exactly-once effects across unrelated systems merely because a workflow is durable.

Test interruption at each effect boundary, repeated callbacks, crash after success before persistence, malformed model output, tool refusal, budget exhaustion, and cross-tenant run access. For graph changes, test restore from old checkpoints. For durable workflow changes, test history replay and the platform's supported versioning strategy before rollout.
