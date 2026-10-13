---
name: aio-prototype
description: "Run a bounded backend architecture spike to resolve a specific technical uncertainty."
---

# AIO Prototype

Run a bounded backend architecture spike to resolve a specific technical uncertainty.

## Protocol

1. State the falsifiable question, competing mechanisms, workload, success threshold and effort/time ceiling. Do not run a spike when existing repository evidence already answers it.
2. Build the smallest isolated experiment needed for the decision, keeping secrets and production data out. Test the actual boundary: replay, query plan, cancellation, concurrency or model/tool budget, rather than a decorative demo.
3. Record commands, versions, raw results and failure cases. Keep stubbed services and synthetic data clearly identified; a passing simulation cannot establish production readiness.
4. Compare alternatives and update the decision record. Preserve useful evidence and explicitly decide whether prototype code is discarded, hardened or reused after proper acceptance tests.

## Return and handoff

A bounded experiment report and architecture decision, with prototype limitations. No automatic production adoption.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
