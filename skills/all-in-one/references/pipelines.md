# Jobs, durable workflows, and data pipelines

Choose execution semantics before a scheduler. Independent short jobs can run directly in workers. Multi-step business operations with durable waits may justify Temporal. Scheduled partitioned transformations with dependencies may justify Airflow. These choices solve different failure and scheduling problems.

## Task contracts and delivery semantics

Each task defines input identity, partition/window, output artifact, validation, dependencies, timeout, retry policy, and cleanup. Use stable operation IDs across retries. Pass large artifacts by reference with checksum and schema version rather than through scheduler state.

Assume a worker can crash after performing an effect and before acknowledging. Design repeatable writes, deduplication, transactional state, or reconciliation. Name the system where the idempotency guarantee holds and how long its keys are retained. Retry is not a substitute for idempotency.

Use one retry owner for a logical boundary. Set an overall deadline and maximum attempts, including client and worker retry settings. Distinguish transient errors from invalid input, permission denial, and poisoned messages. A dead-letter or terminal-failure path needs diagnostics, an owner, and replay rules.

## Durable orchestration

Keep workflow code deterministic under history replay: no direct random numbers, current-clock reads, model calls, HTTP, or database effects unless the SDK supplies a replay-safe primitive. Perform effects in activities. Verify the exact SDK's semantics before adopting new features.

A worker deployment may replay histories created by older code. Use supported patching/versioning or worker routing and retain compatibility while old runs exist. Test old histories, activity timeouts, lost acknowledgements, cancellation, and shutdown while work is in flight.

Use durable workflows only when their recovery contract justifies them. Modern Temporal guidance also supports standalone activities for straightforward background jobs; do not build a signal-driven dispatcher workflow by default.

## DAGs and backfills

Detect cycles, define joins explicitly, and make partition dependencies visible. Specify event time versus processing time, timezone, watermark, late data, and empty partition behavior. A successful upstream task alone does not prove downstream output completeness.

Write to staging or temporary artifacts, validate, then publish atomically where supported. For incremental tables, define merge keys, duplicate handling, and replacement scope. Backfills and scheduled runs may target the same partition: prevent conflicting writes or make their outcomes deterministic.

Choose catchup behavior deliberately. Historical ordering constraints may be valid; document why rather than blindly disabling previous-run dependencies. Limit mapped-task fan-out and simultaneous backfills. Long waiting sensors should release scarce worker capacity using the scheduler's supported mode.

Test repeated partition runs, overlap, late arrivals, partial output, missing upstream data, failed joins, poisoned inputs, and restart. Verify Airflow imports and operator/sensor APIs against the installed major version.
