---
name: aio-canary
description: "Observe a bounded backend canary or post-deploy window against identified baselines, configured thresholds and real functional effects. Use for baseline capture or deployment health checks; rollout and rollback require existing authorization."
---

# AIO Canary

Compare backend outcomes and operational signals across a release window. A successful deploy command or health endpoint cannot establish that real requests/jobs, storage and external effects still work. Use [AIO Observe](../aio-observe/SKILL.md) to establish missing instrumentation and [AIO Release](../aio-release/SKILL.md) for rollout ownership.

Inherit the [stage contract](../all-in-one/references/stage-contracts.md), controller journal and [resource budget](../all-in-one/references/resource-budgets.md); standalone observation resolves thorough by default. Reuse only exact-scope applicable evidence for the accepted source, deployed code/config/dependencies, environment and checks. This operational lens does not automatically launch another independent reviewer or reset the run's limits. Long external monitoring is pending work, not permission to poll past the budget.

Use `--baseline` for capture, `--quick` for one pass, and normal mode for the configured bounded comparison. Read [canary modes](references/modes.md) when selecting or interpreting these operations. Explicit user scope wins; every mode retains the same authority, journal and health evidence conditions.

## Observation contract

Before observing, record the environment/service, deployment ID and observed revision, routing/cohort, affected API/job boundaries, available read-only queries, owner and authorized actions. Separate **baseline capture**, **single-pass health check** and **bounded canary comparison**. Observe/report is the default; the skill itself grants no rollout, traffic change or rollback authority.

Use configured SLOs or the accepted release plan for absolute/relative thresholds, aggregation windows, minimum request/sample counts, signal freshness, transient-confirmation rule and hard-stop conditions. Include actual functional effects and applicable error rate, latency distributions, saturation, queue age/failures, dependency errors and durable state/reconciliation. Check both control and candidate cohorts where available. Empty traffic, mixed revisions, stale metrics or missing required signals cannot produce a green verdict.

Record start/deadline, query timeout, cadence, maximum rounds/samples and retry cap within the controller's remaining budget. Without a selected window, perform one bounded pass and label it a single-pass check. Missing thresholds or baseline comparison policy permits observations, not a certified healthy canary. Do not invent a universal latency multiplier or monitoring duration.

## Capture and compare

For baseline capture, save observed pre-deploy revision/config identity, environment/cohort, timestamps, query definitions/windows, denominators, error identities, metric distributions and representative functional assertions. Preserve the original baseline. A snapshot captured after deployment is a monitoring-start reference and cannot prove pre-deploy health. If no comparable baseline exists, report observations against configured absolute targets and an inconclusive comparison.

Run fresh, bounded rounds with available telemetry/CLI/API tools; no bundled monitor or scheduler is assumed. Record actual deployed identity per round and flag revision drift. Exercise only authorized functional probes with isolated fixture identities and bounded effects; a read-only probe may leave write/effect boundaries unverified. Record expected/actual response, terminal job outcome and relevant persisted/effect evidence, not only request acceptance.

Compare equivalent cohorts, workload, windows and sample counts. Identify new failure signatures rather than just total error counts; retain pre-existing violations of absolute safety targets. Track first occurrence, confirmations, persistence and resolution. Use the configured consecutive-round/window rule for transients; an immediate integrity/security hard stop is not delayed to satisfy a generic two-sample rule. With no transient policy, report observations and do not assert a confirmed healthy comparison.

Never overlap rounds. After a round, wait only the remaining cadence interval, using waits of at most 60 seconds and remaining budget/deadline. Record actual cadence when queries run long. Stop new queries at the deadline, finish or cancel owned operations under their timeout, and checkpoint an incomplete minimum window/sample count. Retrying telemetry access is bounded; unavailable results stay unavailable.

## Action and return

On a confirmed breach or hard stop, report the affected boundary, threshold, baseline/current values, deployed identity and raw evidence promptly. Execute rollout/rollback/reconciliation only within existing environment-specific authority, triggers and runbook; otherwise return the concrete recommended action. Verify the resulting revision and recovery signals after an authorized action. Recovery does not erase the incident from this run's record.

Return scope/identities, actual elapsed window/rounds/samples, query and functional evidence, threshold comparisons, transients, confirmed/resolved incidents and missing coverage. Use **healthy** only when the configured comparable baseline, comparison policy, all required signals, functional assertions, minimum observation window and sample conditions pass; otherwise distinguish **breach**, **inconclusive**, **pending** or **blocked** with the cause. Keep the stage status separate from the health verdict. Update a durable baseline only under accepted baseline-update authority; never overwrite it merely because a round passed. Create persistent monitoring/notifications only when explicitly requested through an available scheduler, and return to the controller.
