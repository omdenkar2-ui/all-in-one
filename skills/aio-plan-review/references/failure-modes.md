# Failure-mode ledger for backend plans

Use this within the existing plan review, not as another audit or reviewer job. Reuse the plan's R requirements, U units and V verifications. Cover new/materially changed paths and affected integration boundaries; select credible failures with consequences rather than enumerate every hypothetical exception.

## Follow a complete path

Trace input/identity -> validation/authorization -> state transition -> durable write or external effect -> response/acknowledgement. For nontrivial async paths, a small flow or state diagram can expose transaction, ownership and restart boundaries; label proposed components separately from source-confirmed behavior. Read relevant callers and tests before drawing conclusions.

For each such path, name a realistic production failure and record a compact row:

| FM ID / R / U | Path and triggering failure | Handling and recovery owner | V / assertion / test layer | Observable failure and recovery | Disposition / evidence |
| --- | --- | --- | --- | --- | --- |
| FM1 / R3 / U2 | Worker effect succeeds; acknowledgement is lost | Retry owner deduplicates the stable effect key | V5: replay does not add another durable effect; integration fault test | Job records retry/terminal state; caller can inspect outcome by run ID | Planned; handler/test locations or unresolved gap |

The observable column names what the API caller, CLI user or operator can actually see: declared status/error, terminal job state, metric/log/alert or documented recovery action. "Log the error" without destination, visibility or a recoverable state does not establish detection. A planned assertion needs a fixture, fault point and oracle; a test name alone is insufficient.

## Select applicable failures

- **Identity/input:** missing or revoked context, wrong tenant/role, malformed downstream/model/tool output. Does rejection preserve the no-effect boundary and avoid leaking resource existence?
- **Effect/durability:** crash or timeout before/after commit, duplicate delivery, partial publication, reordered events and concurrent operations. Which owner retries, which key deduplicates, and what invariant survives? Preserve the documented delivery guarantee; do not invent exactly-once semantics.
- **Recovery/versioning:** cancellation during owned work, restart from checkpoint/history, old schema/state replay and migration rollback. Can partial effects be compensated, reconciled or reported without falsely marking success?
- **Resources/integration:** unavailable provider, rate limit, queue growth, unbounded input/query/cache or retry. Name the limit/deadline/terminal disposition and the load at which a claimed risk matters; do not invent benchmarks.

Check existing shared helpers and caller contracts before adding a layer. Reuse is justified by compatible behavior, errors, effects, security and deployment boundaries; a similar name is insufficient. Proposed abstractions should name real callers, the adoption boundary and the regression assertion they need.

## Readiness and findings

A credible material failure with no handling, no planned test and no observable failure is a critical plan gap. Other missing columns receive severity proportional to the accepted contract and consequence; do not create a blocker merely for a benign hypothetical. Cite the path, source/plan location and failing invariant.

Keep already-tested, planned, blocked, deferred and not-applicable coverage distinct. A mocked provider cannot establish the actual integration; identify the required layer and missing prerequisite. Every proposed test should protect an observable invariant, catch a credible regression and add coverage absent from existing tests; prefer extending a suitable test. Do not demand a production-only seam to expose private implementation.

Carry binding behavior and already-authorized proof into the plan. New product policy or a conflict with a settled decision remains an explicit unresolved decision; the ledger cannot authorize it. Return gaps and concrete planning repairs within the current two-wave/budget contract. A complete ledger or passing plan gate does not prove implementation correctness.
