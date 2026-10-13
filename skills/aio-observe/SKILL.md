---
name: aio-observe
description: "Establish backend and agent telemetry, operational checks and actionable recovery signals."
---

# AIO Observe

Establish backend and agent telemetry, operational checks and actionable recovery signals.

## Protocol

1. Map user/API/job outcomes to service targets and failure boundaries. Inspect existing instrumentation and pick signals that answer operational questions.
2. Correlate request/tenant/job/run/operation IDs without logging unrestricted prompts, secrets or personal data. Measure queue age, attempts, terminal failures, model/tool budgets and external effects where relevant.
3. Define metrics/traces/logs and alerts with thresholds, owner and recovery action. Avoid high-cardinality labels or instrumentation that creates unbounded storage/cost.
4. Exercise a controlled failure and verify a signal appears, identifies the affected boundary and leads to a working runbook. Validate normal traffic and noise/sensitive-data behavior.
5. For requested ongoing monitoring use the host automation/scheduler capability with explicit user scope. A one-time observation must not claim future continuous monitoring.

## Return and handoff

An instrumentation/runbook change or observed health report with actual signals and operational limits.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
