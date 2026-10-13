---
name: aio-agents
description: "Engineer agent state, tool authority, model decisions, budgets and durable checkpoint recovery."
---

# AIO Agents

Engineer agent state, tool authority, model decisions, budgets and durable checkpoint recovery.

## Protocol

1. Read [agent workflows](../all-in-one/references/agent-workflows.md) and the accepted architecture. Define typed state, partial updates/reducers, transitions, terminal conditions and stable run/operation IDs.
2. Separate model proposals from application authorization and execution. Derive tenant/permissions from trusted context, validate tool arguments, scope credentials and treat retrieved text/tool output as untrusted data.
3. Budget model calls/tokens, tools, wall time, concurrency and repair attempts. Define errors, cancellation and terminal status without letting retries create unbounded work.
4. Choose durable state and effect receipts from actual recovery needs. Keep nondeterministic/effectful calls outside replayed workflow logic and reconcile crash-after-effect ambiguity with stable idempotency identity.
5. Use [aio-tdd](../aio-tdd/SKILL.md) and [aio-test](../aio-test/SKILL.md) to exercise invalid model output, reducers/routes, unauthorized tools, budget exhaustion, duplicate effects, old checkpoints and restart.

## Return and handoff

An agent architecture/implementation with state/tool contracts, budget and recovery evidence; no arbitrary tool authority granted by a prompt.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
