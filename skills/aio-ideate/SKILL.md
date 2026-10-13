---
name: aio-ideate
description: "Generate and rank backend or agent-system approaches before committing to a design."
---

# AIO Ideate

Generate and rank backend or agent-system approaches before committing to a design.

## Protocol

1. Establish the operational problem, caller/job, observable failure or opportunity, constraints and accepted scope. Read existing architecture and incidents before proposing new infrastructure.
2. Generate a small set of materially different mechanisms: improve the current service, queue a bounded job, use an explicit agent state machine, or introduce durable orchestration only when its recovery benefit is needed.
3. Rank candidates using correctness, recovery, tenant/trust boundaries, latency/cost, migration risk and the strength of available evidence. Separate known facts from assumptions; state which measurement could reverse the ranking.
4. Recommend a candidate and retain rejected alternatives with reasons. Route uncertain product outcomes to [aio-brainstorm](../aio-brainstorm/SKILL.md), and a settled outcome to [aio-spec](../aio-spec/SKILL.md).

## Return and handoff

A ranked backend decision brief with evidence, alternatives, uncertainties and the recommended next stage. Ideas do not authorize implementation.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
