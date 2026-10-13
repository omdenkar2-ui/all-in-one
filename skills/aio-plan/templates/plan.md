# Backend implementation plan

## Source, outcome and authority

Record the exact canonical source/path/digest, caller/operator outcome, accepted scope, preserved user choices, delivery destination and implementation/deployment authority.

## Repository context

Record inspected runtime and dependency versions, revision, relevant user changes, entrypoints, owned data and current test commands. Link evidence needed by a worker unfamiliar with the codebase.

## Requirements and decisions

Preserve stable `R1` requirements and observable acceptance. Record consequential `D1` decisions with alternatives, evidence, tradeoffs and status. Explain the selected architecture, critical success/failure trace, compatibility and supported resource targets. Do not turn unsupported assumptions into guarantees.

## Unit U1

- Requirement IDs and prerequisite units.
- Single owner and exact create/modify/test file paths.
- Consumed interfaces: names, typed input, result and error contracts.
- Produced interfaces: names, types, versions and downstream consumers.
- Focused failing test: name, assertions, command and expected behavioral failure before implementation.
- Implementation steps that settle the intended behavior without transcribing routine function bodies.
- Passing command and observable acceptance; stable `V1` verification IDs.
- Recovery/security/resource checks relevant to this unit.
- Ownership handoff note if another unit edits the same file.

Repeat units only for separately testable deliverables. Assign integration to the controller and identify which disjoint units can run concurrently.

## Verification and review focus

Map every requirement to units and each unit to verification IDs. List required commands/environments, observable assertions and the risky input/failure classes not covered by a happy path. Distinguish planned checks from observed results. Record independent feasibility/adversarial review findings and actual availability.

## Migration, delivery and recovery

Define schema/API/history compatibility, rollout/backfill, rollback or forward-recovery limits, operator intervention and the authorized destination. Preserve current production data; authorization to implement does not imply authorization to discard it.

## Execution readiness

Record current source/plan digests, structural gate result, semantic review result, remaining blockers and first executable unit. Keep real unknowns visible. A ready plan is the start of execution, not evidence of delivered behavior.
