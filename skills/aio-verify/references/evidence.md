# Evidence selection and freshness

## Choose semantic checks

The contract determines tests; a fixed checklist does not prove every system. Every applicable row needs an observable assertion and the production defect it catches. Avoid tests that merely match headings, duplicate the algorithm, assert private call counts, or reproduce all behavior in mocks.

| Backend change | Evidence that addresses its risk |
| --- | --- |
| API contract | Valid/invalid requests through the real handler and auth chain; schema/error/pagination compatibility; allowed and denied object/tenant access. |
| Persistence | Real database constraints and transactions; concurrent uniqueness; failed transactions; old/new schema compatibility; realistic backfill and rollback/data-preservation observations. |
| External effect | Duplicate request/delivery and concurrent claims; fault immediately after provider success before acknowledgement; durable outcome/reconciliation on restart. A mocked effect alone cannot prove provider idempotency. |
| Durable workflow | Checkpoint round-trip and schema version; replay after each meaningful persisted transition; stale worker/lease handling; cancellation and retry exhaustion without repeated committed effects. |
| Pipeline | Real source-to-sink boundary where practical; duplicates/out-of-order/late/poison inputs; partition/window edges; partial batches and backfills; lineage and dead-letter outcomes. |
| Algorithm | Independent slow/exhaustive oracle on bounded cases, properties and metamorphic relations, boundary/adversarial inputs; profiling/benchmark on a named workload with equal output and resource bounds. |
| Agent | Versioned representative/adversarial evaluation fixtures; validated tool arguments and permissions; injected document/tool instructions; tenant memory isolation; budget/termination; provider timeout and resumed side effects. |
| Release | Production-like build/config, required CI on the exact head, startup/migration/health evidence, rollout metrics and authorized rollback path. |

Use deterministic fakes for uncontrollable external systems only with an explicit boundary and limitations. Verify real interactions at the layers under the team's control. Fault injection and concurrency tests need controlled scheduling or reproducible seeds rather than random sleeps and unrecorded lucky runs.

Tests for behavioral changes should have observed red evidence before production edits. Refactors can start with characterization coverage plus a deliberate discriminating fault or restored prior behavior in an isolated copy to establish that critical assertions can detect the defect. Never reset or delete user work to demonstrate red. If an inherited implementation lacks historical red evidence, report that gap; a safe new regression demonstration is a new observation, not retroactive TDD.

## Record what ran

For every required check record the check ID, requirement IDs, purpose/oracle, exact argv/command, cwd, relevant runtime/dependency/config versions, source snapshot, start/completion times, exit status, full log path and output artifacts. Secret values and sensitive data stay out of logs; recording a version/config fingerprint is different from dumping credentials.

Inspect complete output and test counts. A successful runner may skip an entire integration group or exit green on no discovered tests. Expected failures and warnings require interpretation. A negative-path CLI expected to return nonzero is verified by a wrapper/assertion that passes only when both exit code and diagnostic match the intended failure; do not label a raw exit-1 command as an exit-0 passed check.

When a check fails, classify product regression, known baseline failure, environmental failure or unknown with evidence. Known unrelated failures remain named limitations. Repair within accepted scope and rerun affected checks; a flaky rerun without a causal explanation does not erase the first failure. Stable repeated evidence may support a scoped infra classification, never a fabricated product pass.

## Scope freshness precisely

HEAD identifies only committed source. Track uncommitted diff and relevant untracked files, generated output, configuration and dependency versions. After a change, use the dependency graph to invalidate affected checks: test edits invalidate that test evidence; shared contracts, schema, runtime or dependency changes may invalidate several units. Final integration tests cover composition that focused tests do not.

Use project-required full suites/build/lint/type/migration checks once on the finished integrated state. A prohibitively expensive, unavailable or credential-dependent required suite remains pending/blocked with the actual reason; replace it only when the contract owner authorizes an equivalent criterion. Existing valid evidence can be reused if source, environment and intended assertion remain identical.

## State distinct claims

Local checks passed, independent review completed, PR created, CI passed, merge-ready, deployed, and release healthy are different outcomes. Report each from its own evidence. A no-remote project can have verified local delivery and no PR. A PR can exist while CI is pending. A backend deployment can pass health checks while the mobile submission dossier is incomplete.

Implementation-scope verification is the pre-delivery gate: local acceptance and the required implementation review can pass while delivery remains pending. Completion-scope verification is the post-delivery gate: inspect the requested destination and all applicable final prerequisites before running the final receipt. Keep the prepared pre-delivery receipt blocked/pending rather than demanding final delivery before AIO Ship can perform it. This distinction does not waive unavailable independent review or failed required local checks.

The core checker accepts only its defined receipt schema; keep the richer matrix/ledger as linked evidence instead of adding unknown fields. Map actual required check IDs/results, unit files, review status/findings, blockers and requested delivery into that receipt. Set complete only after the external assertions have been independently observed by the controller; the checker cannot make them true.
