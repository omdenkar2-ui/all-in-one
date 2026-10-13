---
name: aio-qa
description: "Explore backend API, CLI, job, worker and webhook behavior, then repair authorized reproducible defects and verify durable outcomes. Use for backend QA, quick QA or replaying a prior regression report; use aio-qa-only for report-only inspection."
---

# AIO QA

Exercise the selected backend contract and observe actual effects. This stage can diagnose and repair confirmed defects when the user's request authorizes fixes. A report-only request uses [AIO QA Only](../aio-qa-only/SKILL.md). QA is scoped functional work, not a separate whole-project build or shipment.

Inherit the [resource contract](../all-in-one/references/resource-budgets.md), original journal and accepted R/V checks. Use thorough for standalone work. Read [QA modes](references/modes.md) to resolve **Full / Quick / Regression** exploration separately from **Quick / Standard / Exhaustive** fix tiers. Defaults are Full exploration and Standard repairs within accepted scope. These names select work; they do not change the resource profile or erase mandatory acceptance.

## Protocol

1. Bind the exact source and selected API, CLI, job, worker or webhook contract. Reuse valid current-source probes. Record user authority, fixtures, expected initial/final state and remaining budget. A command's success or an accepted/enqueued response is insufficient evidence of the final business effect.
2. Resolve mode conflicts before dependent probes. For Regression, inspect the actual previous report and replay inputs; validate contract, fixture, environment and revision applicability. Previous buggy behavior is not an oracle. Missing prerequisites are explicit coverage gaps; do not silently call a new Full sweep a regression replay.
3. Use [AIO Test](../aio-test/SKILL.md) and its [functional contracts](../aio-test/references/functional-contracts.md) to exercise relevant success, authorization, malformed input, retry, duplicate, concurrency, cancellation and crash/recovery boundaries. Use repository-native tools and disposable environments. Avoid unrequested test-framework installation or external side effects. Require real storage/provider evidence for claims that depend on it.
4. Retain each observed issue's expected/actual effect, stable finding ID, severity, source, exact reproduction and limits. Inspect failures before assigning product blame; fixture and cleanup defects need their own diagnosis. Report skipped or unavailable checks and unmapped requirements separately.
5. For authorized fixes within the selected tier, use [AIO Debug](../aio-debug/SKILL.md) for a falsifiable cause and [TDD](../aio-tdd/SKILL.md) for the observed failing regression before implementation. Assess capacity and reserve the run's next repair wave before corrective changes. Combine compatible repairs rather than creating a wave per finding. Respect shared file ownership and at most two aggregate waves across the run.
6. Rerun affected probes and accepted checks against the actual integrated source. Obtain missing required independent review through the existing controller; current-source matching evidence can be reused. Mandatory blockers cannot be deferred into a green QA result because Quick excluded their fix severity or the budget ended.

## Return and handoff

Return selected exploration/tier, tested contracts, command logs, initial/final durable effects, fixed/still-failing/new findings, untested requirements and actual status. A clean scoped QA result establishes only its observed coverage. Launch readiness and delivery require their own accepted evidence.

Follow the [stage contract](../all-in-one/references/stage-contracts.md). Return to the integrating controller for verification and delivery; QA does not create another shipping loop. Save unresolved work with exact replay instructions when a required prerequisite or budget is exhausted.
