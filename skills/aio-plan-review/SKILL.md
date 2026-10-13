---
name: aio-plan-review
description: "Check a backend implementation plan for requirement coverage, feasibility and adversarial failures."
---

# AIO Plan Review

Check a backend implementation plan for requirement coverage, feasibility and adversarial failures.

Inherit the [resource contract](../all-in-one/references/resource-budgets.md) and journal; resolve thorough for a standalone review. One independent reviewer job normally performs both plan lenses using a bounded packet and relevant raw source. Reserve it with stable stage scope `PLAN` before dispatch, record actual plan coverage, and reuse a matching source/plan review at the controller handoff rather than repeating it.

## Protocol

1. Load the exact human plan, machine plan and accepted source. Use [aio-plan](../aio-plan/SKILL.md) and the bundled plan gate; malformed or stale plan data cannot establish execution readiness.
2. Review requirement-to-unit-to-verification coverage, dependency order, owned files, consumers/producers, migration and rollback. Check relevant existing solutions and callers before proposing new machinery. Identify concrete gaps rather than requesting generic extra detail.
3. Conduct separate feasibility and adversarial analytical passes, normally in one independent job. Use the [failure-mode ledger](references/failure-modes.md) for new or materially changed paths: link realistic failures to handling, R/U/V coverage and an observable caller/operator outcome. Trace crash after effect, duplicate event, unauthorized tenant, invalid model/tool result, old state/schema replay and resource exhaustion when applicable. Additional jobs require distinct uncovered scope and budget.
4. Use fresh independent reviewers where available. A controller self-check is useful but is not independent review. Check findings against repository evidence and preserve source locations and consequences.
5. Return findings by default. Apply planning repairs only within authorized scope and the run's two-wave ceiling, then rerun affected gates/review. Escalate settled-decision conflicts. Return ready evidence to the caller; authorized execution may continue through [aio-work](../aio-work/SKILL.md). Unmet review/budget prerequisites remain checkpointed blockers, never invented readiness.

## Return and handoff

An execution-readiness report with coverage gaps, stable finding IDs, failure-mode ledger, review scope and status. Proposed tests and diagrams are planning evidence, not executed verification. Do not implement while reviewing a plan.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
