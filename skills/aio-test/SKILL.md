---
name: aio-test
description: "Design and run backend boundary tests, fault injection and independent correctness oracles."
---

# AIO Test

Design and run backend boundary tests, fault injection and independent correctness oracles.

Inherit the caller's [resource contract](../all-in-one/references/resource-budgets.md) and journal; use thorough for a standalone run. Select checks from accepted behavior and the changed failure boundaries; do not expand a bounded smoke/regression request into full exploration. For requested functional exploration use [Full / Quick / Regression](../aio-qa/references/modes.md); those selectors preserve all accepted required checks. [AIO QA](../aio-qa/SKILL.md) coordinates authorized repair, while Test returns probes and evidence to its caller.

## Protocol

1. Map tests to R/V IDs, actual interfaces and failure boundaries. For API, CLI, jobs, workers or webhooks, read [functional contracts](references/functional-contracts.md) and select applicable probes using repository-native tools. Separate unit, integration, fault/recovery and load evidence; identify unavailable providers or credentials before declaring coverage.
2. Vary inputs and state adversarially: malformed payloads, revoked context, cross-tenant IDs, repeat events, timeouts after commit/effect, partial publication, restart/replay and cancellation.
3. Use temporary real storage or the repository test harness for persistence/concurrency invariants. Mocks can control faults but cannot prove a real provider or database integration works.
4. For algorithms, compare results with an independent reference over bounded exhaustive/random inputs and verify tie/error semantics. For resource targets measure a representative distribution, not one favorable request.
5. Execute the selected suites and inspect assertions, final effects, failures, skips and exit codes. Preserve reproducible probes and honest coverage states. Diagnose fixture/cleanup failures using the reference before assigning product blame. Report uncovered requirements and reproducible failures to [aio-debug](../aio-debug/SKILL.md); successful results go to [aio-verify](../aio-verify/SKILL.md).

## Return and handoff

A requirement-linked test report with actual commands/results, initial/final state, fixtures, fault points, coverage states and remaining gaps.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
