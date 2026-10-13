---
name: aio-explain
description: "Explain a backend or agent workflow from actual code, state, data and failure boundaries."
---

# AIO Explain

Explain a backend or agent workflow from actual code, state, data and failure boundaries.

## Protocol

1. Trace the real entrypoint through validation/authorization, service/state, storage/queue/tool effects and outcome. Name source locations and distinguish observed code from inference.
2. Explain state ownership, retries, acknowledgement, replay, tenant boundaries and termination using one representative success and relevant failure trace.
3. Use a small diagram when it exposes ownership/transition or concurrency, and state unknown integrations/version assumptions. Avoid claiming implementation that is only planned.
4. Answer the requested question at the reader's level. Read-only explanation ends with the answer and does not launch implementation or publication.

## Return and handoff

A code-grounded explanation with source references and explicit uncertainty.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
