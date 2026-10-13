---
name: aio-brainstorm
description: "Explore ambiguous backend, API, agent or workflow ideas into a bounded requirements brief with alternatives and observable success. Use before architecture or planning when the outcome or scope is unsettled."
---

# AIO Brainstorm

Determine what must become true for callers or operators before selecting how to build it. Preserve the user's backend scope, existing stack, constraints and already granted autonomy. A brief can be a short answer; substantial work needs stable requirements that travel into the implementation plan.

Inherit the caller's [stage contract](../all-in-one/references/stage-contracts.md), [resource budget](../all-in-one/references/resource-budgets.md) and original journal; use thorough for a standalone run. Default to **HOLD SCOPE**. For a named scope mode or proposed addition/deferral, read [scope modes](references/modes.md). Explicit user instructions govern; a mode does not approve a requirement change or production implementation.

## Establish the brief

1. Read the named source, relevant repository contracts and current interfaces. Separate observed facts, user decisions and hypotheses. Resolve repository facts through inspection rather than asking the user to look them up.
2. State the outcome, affected actors and exclusions. Distinguish an implementation suggestion from the outcome it serves. An agent framework, queue or vector database is a means, not success.
3. Read [backend discovery](references/discovery.md) for an ambiguous workflow. Ask only questions that materially change the outcome, safety or irreversible scope. Carry settled choices forward; new evidence of infeasibility earns an explicit blocker, not a silent replacement.
4. Compare plausible alternatives against the same acceptance criteria, including the least complex option. Explain carrying cost, failure behavior and reversibility. If a decisive claim needs an experiment, route a bounded question to [AIO Prototype](../aio-prototype/SKILL.md); do not disguise a guess as a decision.
5. Record accepted requirements as stable `R1`, `R2` IDs with observable acceptance, provenance and real uncertainties. Use [brief template](templates/brief.md) when a durable artifact helps later workers. Omit irrelevant sections; do not inflate a narrow change into a platform project.

## Ready for planning

A planner must be able to identify the goal, scope, inputs/outputs, constraints, success conditions and unresolved decisions without inventing product behavior. Do not call an incomplete brief executable. For architecture-intensive work, hand it to [AIO Architecture](../aio-architecture/SKILL.md); an established brief goes to [AIO Plan](../aio-plan/SKILL.md).

A standalone brainstorm writes only its requested brief and reports the next useful step. In an already authorized build or Complete Destruction run, return the brief, stable source path, readiness and blockers to the controller, which continues without another routine approval. Do not implement production code inside this skill.
