# Backend verification and evidence

Choose evidence from the contract's failure boundaries. A list of commands in a document is a plan, not a test result. Run the checks, inspect outputs, and record the exact revision/source, environment, command, exit status, artifact, and relevant assertion.

## Select meaningful tests

| Boundary | Evidence |
| --- | --- |
| HTTP/RPC API | Valid/invalid input, auth, status/error schema, deadlines |
| Database | Constraints, races, rollback, migration compatibility, actual roles |
| Queue or external effect | Repeated delivery, crash after effect before acknowledgement, retry exhaustion |
| Agent state | Transition/reducer tests, invalid tool output, budget stop, restart/checkpoint recovery |
| Durable orchestrator | History replay, activity failures, version transition, cancellation |
| DAG | Repeated/overlapping partitions, late data, join behavior, partial publish |
| Algorithm | Oracle comparisons, adversarial cases, time/space bounds |
| Resource target | Representative load, latency distribution, throughput, memory/error rate |

Use test-first failure evidence for defects and risky behavior. Tests should assert outcomes and invariants rather than mirror implementation details. Keep unit, integration, and operational evidence distinct; passing mocks does not establish a production integration works.

## Review

Give a fresh reviewer the accepted contract, precise change scope, dependency versions, and test evidence. Ask for concrete failures with reproduction or reasoning tied to current code. Resolve factual disputes by inspecting the implementation. Confirm fixes with relevant tests; do not rerun unrelated suites without cause.

An unavailable reviewer is a limitation, not a completed review. A receipt claiming full completion requires independent review; a narrower user-requested task can still be delivered honestly with the limitation disclosed and without a complete receipt.

## Receipt checker contract

The helper accepts a JSON receipt and an explicit workspace root. Paths are relative to that root and must resolve to existing files inside it. It hashes the named source, requires completed units and evidence for required checks, rejects blockers/open blocking findings, and checks delivery evidence. The template begins blocked because nothing has run.

Evidence files are caller-produced records. The checker never executes recorded commands, authenticates logs, contacts a remote, or proves correctness. External delivery requires separate inspection of the actual PR/deployment. Store truthful records and do not create arbitrary files solely to satisfy validation.

A complete receipt has schema_version 1, status complete, source path/sha256, completed units with files, nonempty required_checks covered by passed checks with command/exit_code/evidence, completed review with findings, no blockers, and completed delivery with evidence. External delivery also records an HTTPS URL.

## Terminal states

Report complete only for the accepted scope and requested destination with actual verification. If a required integration, credential, reviewer, or operational check is unavailable, save the working state, report the limitation, and identify the next action. Neither retry exhaustion nor a local static check can turn unmet acceptance into success.

## Focused execution stages

Use [AIO Test](../../aio-test/SKILL.md) for functional API/CLI/async contracts, [AIO Verify](../../aio-verify/SKILL.md) for bounded checker evidence, [AIO Test Audit](../../aio-test-audit/SKILL.md) for demonstrated suite-value concerns, and [AIO Devex Review](../../aio-devex-review/SKILL.md) for affected developer journeys. These are conditional lenses sharing the run budget, not four mandatory jobs.
