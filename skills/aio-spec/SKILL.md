---
name: aio-spec
description: "Turn accepted backend behavior into versioned requirements, interfaces and acceptance criteria."
---

# AIO Spec

Turn accepted backend behavior into versioned requirements, interfaces and acceptance criteria.

## Protocol

1. Read the exact request/design and current APIs, event schemas, persistence and consumers. Preserve settled scope; do not silently add features or change the public contract.
2. Assign stable R IDs to observable requirements and V IDs to verifications. Define authentication context, input bounds, success/error behavior, status transitions, consistency, deadlines and compatibility.
3. For jobs or agents, define effect/acknowledgement boundaries, stable operation identity, replay behavior, cancellation, budget exhaustion and terminal errors. Distinguish acceptance from completion.
4. Name nonfunctional targets with units and workload assumptions, data retention and tenant invariants, and the operational owner. Unknown business facts remain explicitly unresolved.
5. Write the contract and a requirement-to-verification matrix. Send a ready contract to [aio-architecture](../aio-architecture/SKILL.md) or [aio-plan](../aio-plan/SKILL.md); planning does not invent missing acceptance.

## Return and handoff

A source-linked backend contract, R/V matrix, scope and unresolved questions. Standalone invocation ends with the spec.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
