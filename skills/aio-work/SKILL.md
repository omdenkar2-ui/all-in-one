---
name: aio-work
description: "Implement an accepted backend plan or concrete build request through test-first units, ordered spec and risk reviews, and integrated verification. Use for backend execution or resuming an exact implementation run; use aio-debug for unexplained failures."
---

# AIO Work

Execute all accepted backend units continuously. A plan, worker success message, or green focused test is not the deliverable. Preserve existing authorization, settled decisions, the chosen stack, and user changes.

Inherit the controller's [resource contract](../all-in-one/references/resource-budgets.md) and journal; a standalone run resolves thorough by default. Check/reserve policy events before new workers, reviews or repair waves. Keep units meaningful rather than per-file, load only relevant guidance and give bounded packets with raw artifact paths. Budget exhaustion returns a checkpoint, never a reset or an early complete verdict.

Resolve the exact work source first. A supplied plan path alone can be a request to explain or review it; implementation requires implementation intent. For a new substantial build, use [AIO Plan](../aio-plan/SKILL.md) to establish the contract and units. A narrow nonbehavioral edit can proceed directly with proportional verification.

Read [execution and recovery](references/execution.md) before dispatching or writing substantial units. It governs the source-bound ledger, ownership, scheduling, worker evidence, and canonical integration. Use the [unit packet](templates/unit-packet.md) to give a fresh worker its own requirements and interfaces rather than the entire conversation. When requested, apply [Careful / Freeze / Guard](references/scope-guards.md) to the original run and worker ownership; these are agent procedures, not installed command-blocking hooks.

For each unit:

1. Inspect its actual code, existing tests, dependencies, and acceptance. Reuse a completed matching capability instead of implementing it again.
2. Use [AIO TDD](../aio-tdd/SKILL.md) for behavior changes: observe the intended red failure before production changes, implement green, then refactor while green. Capture commands, failure reason and source identity as the work happens. No-test exceptions require a nonbehavioral reversible change and suitable replacement verification.
3. Inspect the worker's actual changed files and logs. Run controller-owned checks on the integrated tree. Reject unowned edits, missing evidence, failed checks, and stale source snapshots.
4. Run [AIO Review](../aio-review/SKILL.md) independently. For a bounded unit, use **spec-then-risk** in one job on a frozen snapshot: separate verdicts, spec first, no risk pass while spec is blocked. Separate spec/risk jobs remain possible for justified larger scope and consume the same caps. Self-review is not independent review.
5. Apply confirmed blockers in a reserved corrective wave, rerun affected checks and request scoped re-review within the inherited caps. Allow at most two aggregate repair waves per run. When exhausted, save a resumable blocker and exact next action; mandatory correctness/security/recovery evidence cannot be waived.
6. Mark the unit complete only after its acceptance and required checks pass and findings are resolved. The canonical integrator owns scoped commits and ledger transitions.

After all units, run missing whole-change review and [AIO Verify](../aio-verify/SKILL.md) in implementation scope. Reuse current-source review only when it explicitly covers the complete accepted diff, integration boundaries and deferred findings; unit-only review is insufficient. Do not repeat valid checks merely at a new handoff. Standalone work uses [AIO Ship](../aio-ship/SKILL.md), then completion verification after observed delivery. Under another controller, return evidence without starting another shipping run or closing its receipt. A small thorough run normally needs two review jobs, not every AIO skill.

Return actual status: completed, blocked, or needs-context. Keep useful independent work moving when a unit is blocked, but do not build dependent units on an unresolved contract defect. Independent review unavailable remains explicit and cannot be forged into a complete receipt.
