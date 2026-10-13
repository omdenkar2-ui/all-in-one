# Data and PostgreSQL

Model invariants in the schema as well as application validation. Use appropriate types, primary/foreign keys, unique constraints, and checks. 'Read then insert if absent' is race-prone; use a database-enforced uniqueness rule and atomic insert/upsert behavior.

## Transactions and concurrency

Keep transactions short. Do not hold database locks while waiting for a model, HTTP API, or user response. Split external work from committed state with explicit pending/completed states or an outbox where required. Specify isolation behavior and test the races that matter.

Acquire locks consistently to reduce deadlocks, and handle serialization/deadlock retries within a bounded owner. For queues built on PostgreSQL, understand `SKIP LOCKED` fairness and starvation; it is not a general promise of ordered processing. An advisory lock only coordinates clients that follow the protocol.

Budget connections across all replicas and processes. Validate transaction/session pooling compatibility, prepared statements, and session-dependent state. Protect administration and recovery capacity from application saturation.

## Query shape and evidence

Start from actual queries, cardinality, selectivity, and ordering. Use a composite index matching predicates and ordering where justified; consider partial/covering indexes only with a measurable benefit and write/storage cost. A sequential scan can be correct for small tables or broad queries.

Inspect `EXPLAIN` first. `EXPLAIN ANALYZE` executes the query, including mutations, so choose a safe environment and transaction strategy before using it. Record plans with realistic data and refresh statistics when stale. Do not prescribe index changes from an empty development table.

Use keyset pagination when stable traversal and deep-page performance matter. Include a unique tie-breaker and specify behavior under concurrent inserts/updates. Offset pagination can remain appropriate for small datasets or explicit page-number requirements.

## Tenant isolation and migrations

Treat row-level security as a defense with specific role semantics. Test actual application roles and cross-tenant reads/writes; elevated owner/service roles may bypass policy. Do not derive tenant identity from arbitrary request JSON. See the security playbook for authorization and agent tool boundaries.

For compatibility-sensitive migration, expand schema first, deploy compatible reads/writes, backfill in bounded batches, verify counts/invariants, then contract only after old consumers are retired. Assess locks, statement timeouts, disk, lag, and restart behavior. A backup is useful only if restore is tested.

Test simultaneous duplicate writes, transaction rollback, lock conflicts, pool exhaustion, failed backfill restart, old/new application compatibility, and unauthorized rows. Record the exact database version and migration recovery instructions.
