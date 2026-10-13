---
name: aio-architecture
description: "Design backend and AI agent execution architecture with typed state, authority boundaries, durable recovery, interfaces and resource budgets. Use for consequential architecture choices or workflow design before implementation."
---

# AIO Architecture

Choose the least complex execution model that satisfies the actual requirements. Inspect the current stack and trace an existing request before proposing a replacement. Use [core architecture](../all-in-one/references/architecture.md) for service boundaries and [architecture decisions](references/architecture-decisions.md) for agent and durable-workflow choices.

## Design from a critical trace

1. Read the canonical brief/spec and preserve its `R` IDs. Name actors, trust boundaries, data owners and the externally observable completion contract.
2. Compare the current design and viable alternatives using the same workload, failure conditions and acceptance targets. Record consequential choices, rejected options and evidence in [architecture template](templates/architecture.md). New technology needs a requirement-based reason.
3. Define exact input/output schemas, versioning, state transitions, reducers, stable run and operation identities, authorization checks and retry ownership. Separate model proposals from the controller's permission to execute tools.
4. Trace one successful request and its most dangerous interruption: an external effect succeeds before durable acknowledgment. Name stored facts, retry/reconciliation decisions, allowed terminal states and observable proof. Include duplicate delivery, cancellation and tenant mismatch where applicable.
5. Budget latency, concurrency, storage, model/tool spend and retries. Define overload behavior and operator recovery. Establish schema/API migration, deployment compatibility and rollback conditions.
6. Resolve architecture-level uncertainties through evidence or a bounded [AIO Prototype](../aio-prototype/SKILL.md). Return the chosen contract and failure tests to [AIO Plan](../aio-plan/SKILL.md). Significant cross-boundary designs require fresh feasibility/adversarial inspection in [AIO Plan Review](../aio-plan-review/SKILL.md).

Standalone architecture work changes only its requested design artifact. In an authorized implementation pipeline, return decisions and blockers to the controller; do not add routine approval gates. Do not infer deployment, provider account creation or frontend scope from an architectural diagram.
