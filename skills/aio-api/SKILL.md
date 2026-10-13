---
name: aio-api
description: "Build or evolve backend API, webhook and event contracts with security and compatibility checks."
---

# AIO Api

Build or evolve backend API, webhook and event contracts with security and compatibility checks.

## Protocol

1. Read the accepted contract and real consumers. Define typed inputs/outputs, status/error schema, pagination/order, authentication context, deadline and payload bounds.
2. Enforce authorization for the specific resource/action outside caller or model-supplied identifiers. Validate inputs before expensive work and keep transport separate from domain effects.
3. For writes/webhooks specify idempotency scope and retention, signature/replay handling, acknowledgement and timeout-after-success behavior. A successful enqueue is not a completed job.
4. Use [aio-tdd](../aio-tdd/SKILL.md) for behavioral changes. Exercise invalid input, denied access, duplicate requests/events, deadline/cancellation and affected old consumers.
5. Document compatibility and migration of clients/events. Return the implemented boundary and evidence to the integrating controller; do not redesign unrelated clients.

## Return and handoff

A versioned API/event boundary, implementation, compatibility notes and observed contract tests.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
