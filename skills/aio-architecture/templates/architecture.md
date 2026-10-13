# Backend architecture decision record

## Source and constraints

Name the canonical work source, preserved `R` IDs, inspected stack versions and applicable user decisions. Record workload evidence, capacity assumptions and required delivery scope.

## Selected execution model

Compare current and viable alternatives. Record `D1` with the chosen model, rejected option, supporting evidence, carrying cost and reversibility.

## Boundaries and interfaces

Identify each component's data/behavior ownership, consumed/produced types, trust boundary and compatibility version. A small diagram is useful only if it exposes these boundaries.

## State and authority

Define state fields, reducers, legal transitions, request/run/attempt/operation identities, tenant binding, controller authority and constrained tool contracts.

## Critical trace

Trace a successful operation and an interruption after external success but before acknowledgment. At each step record durable facts, owner, recovery action and observable result. Include terminal failure, cancellation and uncertain outcome semantics.

## Budgets and operations

Record supported deadline/concurrency/retry/storage/model/tool limits, overload response, redacted telemetry, alert owner and intervention procedure. Link assumptions to a validation unit.

## Change and proof

Describe versioned API/schema/history changes, migration/backfill, rollout/rollback constraints and the test that proves each critical invariant. Record unresolved decisions without declaring the design ready.
