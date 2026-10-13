# Execution contract

## Preserve the source

Use the exact source the user or controller supplied. Record its digest and relative path alongside inspected runtime/dependency versions, repository revision and relevant dirty files. A changed source requires reconciliation of affected decisions, requirements and units before execution; a new digest cannot silently bless a changed scope.

One maintained narrative carries the outcome and decisions; `plan.json` indexes executable coverage and dependencies. Do not maintain contradictory scope across several competing documents. Preserve existing IDs across revisions and add new IDs instead of renumbering completed work.

## Stable units, concrete interfaces

Each unit is the smallest deliverable a reviewer could meaningfully accept or reject on its own. Setup, fixtures and documentation belong with the behavior that needs them. Split by responsibility, testability and independent file ownership, not by an arbitrary number of lines or by technical layer.

For each `U1` record its title, covered `R` IDs, preceding `U` IDs, single owner, exact new/modified/test files, inputs and outputs. Interfaces include real names, parameter/result types, field names, errors and compatibility version where consequential. Workers see the source and the interfaces of dependencies; they should not have to guess neighboring workers' symbols.

Shared file edits are sequential. Both units declare an ownership note describing the handoff, and one depends transitively on the other. A controller integrates, inspects diffs and creates canonical commits. Parallelize only ready units with disjoint ownership and settled interfaces; a subagent reporting “done” is not an acceptance check.

## Observable verification

Give each `V1` its owning unit(s), exact command, working directory if needed, environment prerequisites and concrete assertions. A command can be recorded before it is runnable; never claim it was executed. Where production behavior changes, include the focused test's expected pre-change failure and post-change pass. Verify that the failure would expose the defect or missing contract rather than an unrelated environment error.

An acceptance check states the actual invariant: “duplicate delivery after provider success produces one business operation and the same result,” not “idempotency works.” Tests may use controlled adapters/fault injection to establish failure boundaries. Distinguish an adapter simulation from a live-provider integration. Required live checks remain unverified when credentials or an environment are absent.

An algorithm unit needs a supported correctness oracle, relevant edge/input classes and complexity/resource bounds. A performance claim needs workload/distribution, baseline, reproducible measurement and explicit threshold. Schema changes need old/new compatibility, data transformation and a restore or forward-recovery check appropriate to the migration.

## Architectural failure coverage

Select the risks implied by the source rather than attaching every possible test to every unit. Assign the strongest untested risks to specific owning units: duplicate requests, timeout after successful commit, restart/replay, concurrent state updates, untrusted tool arguments, cross-tenant reads/resume, retry/budget exhaustion, cancellation or old workflow histories after deployment.

Name missing coverage and why it matters. “Not applicable” needs a contract-based reason; an inconvenient test is not inapplicable. An unknown resource target becomes an experiment/unit and a binding decision if correctness depends on it.

## Review and rollout

The plan includes deployment compatibility, staged rollout, migration/backfill, rollback limitations and ownership of intervention. Local implementation authority does not imply public deployment authority.

Run a proportional self-check for requirement coverage, matching interfaces, coherent steps and unnecessary complexity. Then obtain independent semantic review through AIO Plan Review: feasibility checks the stack/interfaces/commands; the adversarial lens tests assumptions, authority and critical failure traces. Findings name a requirement, unit or decision and the evidence that would resolve them. If reviewers are unavailable, preserve that state and continue only work whose authorization and uncertainty allow it; do not declare the final plan independently reviewed.
