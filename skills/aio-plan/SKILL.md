---
name: aio-plan
description: "Create an execution-ready backend implementation plan with stable requirements, owned units, exact interfaces, test-first verification and a dependency graph. Use for multi-step backend, agent, pipeline or algorithm work before changing production code."
---

# AIO Plan

For coordinated automatic scope/developer-interface planning with engineering review last, use [AIO Autoplan](../aio-autoplan/SKILL.md) within the existing run. A direct plan request continues to use this focused stage; do not recursively start Autoplan from its child stages.

Turn the exact accepted source into instructions another worker can execute without inventing interfaces, acceptance or scope. Preserve an existing plan and its IDs when deepening it; never substitute a nearby or newer unrelated file. Prior brainstorming is useful when requirements are unsettled, not a mandatory ceremony for an adequate source.

Inherit the [resource contract](../all-in-one/references/resource-budgets.md) and journal, or resolve thorough for a standalone run. Create meaningful delivery units, not one unit per file or planning ritual. Load only relevant source/architecture guidance and budget review before spending the run's remaining capacity. No budget limit waives security, recovery or required acceptance.

## Build the execution contract

1. Read the canonical brief/spec, relevant implementation, current stack and repository instructions. Record the source path and SHA-256, current revision/user changes, relevant files, test commands and delivery authority. Inspect version-sensitive behavior in the installed code or official docs. Planning may run read-only inspection; it does not implement production code or claim tests have passed.
2. Preserve stable `R` requirements and consequential `D` decisions. If the goal remains ambiguous, use [AIO Brainstorm](../aio-brainstorm/SKILL.md); for unresolved cross-boundary design, use [AIO Architecture](../aio-architecture/SKILL.md). Compare alternatives only where the choice matters. Resolve reversible implementation details from evidence within authorization.
3. Read [execution contract](references/execution-contract.md). Write one proportional narrative using [plan template](templates/plan.md), plus `plan.json` from the [blocked starter](templates/plan.json) for substantial executable work. Each `U` unit owns exact files, consumes/produces explicit interfaces, has acyclic dependencies and ends in a separately checkable result.
4. Specify meaningful red/green checks for changed behavior: test name/assertions, exact command and expected failing observation before implementation, then the passing observation. Add recovery, security and resource tests required by the source. Do not create tests solely to match generated prose, or invent observed red/green results during planning.
5. Map R/U/V coverage and validate [structural readiness](references/plan-schema.md), then use [AIO Plan Review](../aio-plan-review/SKILL.md). One independent job normally checks feasibility and adversarial lenses. Reuse matching review evidence at handoff; source/decision changes reopen affected checks. Authorized corrections share the run's two-wave ceiling. Structural validity or exhausted budgets cannot establish execution readiness.

## Handoff

Return the canonical artifact paths/digests, ready or blocked status, review evidence, resolved assumptions and first executable unit. Unavailable independent review stays visible and blocks a claim of independently reviewed readiness; do not relabel self-review as independent.

A standalone plan request ends at its requested artifacts. An already authorized build or Complete Destruction run continues through [AIO Work](../aio-work/SKILL.md) once the contract and required reviews are ready. A source path alone is not implementation authority, and routine phases do not ask for the same authorization again.
