---
name: aio-qa-only
description: "Report-only backend functional QA using Full, Quick or Regression exploration. Reproduce defects and retain evidence without repairing code, changing dependencies or shipping. Use for qa-only, an inspection-only QA report or verifying a previous failure report."
---

# AIO QA Only

Apply [AIO QA](../aio-qa/SKILL.md) with a **report-only** policy. Preserve the same [resource contract](../all-in-one/references/resource-budgets.md), original journal, selected [exploration mode](../aio-qa/references/modes.md), contract expectations and honest coverage. Default Full covers only the selected backend surface; no fix tier applies.

Inspect source and execute authorized isolated probes. Write owned evidence reports and disposable fixtures where appropriate. Do not edit production code, tests, dependencies, persistent configuration or the plan to make a result pass; do not commit, publish or start a repair/shipping controller. State-changing probes require an authorized isolated target and cleanup. If a safe fixture cannot be established, report the affected check as blocked.

Return actual commands, source-bound expected/actual effects, reproducible findings, fixed/still-failing/new classifications for a regression replay, skips and missing requirements. A proposed remedy is a recommendation, not an applied repair. Source-only review and mocks retain their evidence limits.

The report-only invocation ends with its report or returns to the existing controller. If the trusted user request also explicitly authorizes repairs, resolve that intent by routing repair work to AIO QA within the same journal; do not silently mutate under a QA Only label or demand redundant permission. Required acceptance remains unresolved until the corresponding work is actually verified.
