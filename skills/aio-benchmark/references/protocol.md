# Fixed backend comparison

Select one realistic backend task with measurable behavior: for example, a tenant-scoped durable job API with duplicate delivery and crash recovery. Freeze the same task and independent evaluator before producing condition artifacts. The evaluator must exercise real correctness, security and recovery behavior; syntax checks alone cannot fill those gates.

Declare two or three unique conditions chosen from `aio`, `compound-engineering` and `superpowers`. The starter uses `aio` and `compound-engineering`; add `superpowers` only when that workflow is requested. Keep model, reasoning, token allowance, available tools, runtime, task inputs, trial seeds and evaluator equal. The runner records these declared settings but does not enforce or authenticate model generation. The controller records actual settings and any deviation in the comparison report. Randomize condition order or alternate it across repeated trials to reduce ordering effects. All declared trials are retained, including failures.

If the caller selects a budget profile such as Thorough, record the same profile and generation/review token limits for every condition before freezing. The controller must enforce any hard limits using the available model host and retain actual usage observations, or state when enforcement or usage is unavailable. This local evaluator runner neither launches models nor enforces or attests their token budgets.

## Definition schema

`schema_version` is integer 1; `status` becomes `ready` only after the evaluator and assertions are settled. Required fields are `title`, workspace-relative existing `task` and `evaluator` file paths, two or three unique supported `conditions`, nonempty `trials` with unique `id` and integer `seed`, a nonempty `settings` object, all three `gates` (`correctness`, `security`, `recovery`), nonempty `metrics` with unique `id` and `direction` (`lower` or `higher`), and nonempty `assertions` strings. A single condition, duplicate condition or unknown condition ID is rejected. Unknown fields are rejected. Settings are recorded metadata, not an execution plan. Definition JSON cannot contain executable commands.

`freeze` creates a new file without replacing an existing one. It stores task/evaluator SHA256 values, canonical definition digest and freeze time. Freeze before creating the comparison's condition outputs. The runner cannot prove the chronology of files the caller created elsewhere; the controller owns that protocol obligation.

## Evaluator and collection

The caller supplies an explicit argument vector after `--`; shell interpretation is disabled. Include the frozen evaluator's path as an argument, normally `python evaluator.py artifact.py`. The runner checks the task and evaluator digests before collecting. It sets `AIO_BENCHMARK_ARTIFACT`, `AIO_BENCHMARK_TASK`, `AIO_BENCHMARK_CONDITION`, `AIO_BENCHMARK_TRIAL` and `AIO_BENCHMARK_SEED` for evaluators that choose environment-based inputs. The evaluator should accept the artifact path from the caller or that environment variable. It must perform checks without modifying the task, evaluator or artifact.

The evaluator writes one JSON object on stdout:

```json
{"gates":{"correctness":true,"security":true,"recovery":true},"metrics":{"latency_ms":4.2},"notes":[]}
```

All gates must be booleans; every declared metric must be a finite number with no extra metrics. `notes` is a list of strings. Duplicate JSON keys are invalid. A nonzero exit, timeout, malformed result, excessive stdout/stderr, or input mutation produces a failed collection record. A false gate is a valid measured failure, not a successful condition. The runner captures at most 1 MiB per output stream, counts discarded bytes, records output hashes of captured bytes, and kills the evaluator's process group/tree on timeout where the host supports it. Isolated execution remains necessary; a timeout is not a general security sandbox.

For a test evaluator that prints `{total,passed,failed,errors,categories,tests}`, freeze `score_format: "test-report"` and `gate_categories`, an object mapping each of correctness/security/recovery to nonempty lists of category names. Every returned test needs a unique simple `id`, `status` (`passed`, `failed`, or `error`) and a mapped `category`. Counts must agree with individual outcomes. Each gate requires at least one matching test and all matching tests passed. Nonempty evaluator errors fail every gate. Available derived metrics are `total_tests`, `passed_tests`, `failed_tests`, and `pass_rate`; select them in the definition before freezing. Raw evaluator JSON remains in captured stdout. Nonzero-exit reports retain parsed outcomes when valid, while the collection is still failed. Category grouping does not establish that an assertion truly tests the named concern; independent evaluator review remains required.

Collection records preserve definition digest, task/evaluator/artifact hashes, condition/trial/seed, explicit caller argv, observed evaluator elapsed seconds, exit/timeout state, bounded output and parsed result. Elapsed time measures the local evaluator process, not model generation or a whole development workflow. An evaluator's metric is independently measured only to the extent its implementation and raw evidence establish it.

## Comparison

Supply exactly one collection record for every frozen condition/trial pair. Missing, duplicate, foreign-definition or inconsistent records are rejected; no automatic retry or winner selection occurs. Comparison reports all gate outcomes and all collected errors. Metric summaries include every trial for a condition only when all its gates passed. Report count, mean, minimum, maximum and raw values; small samples do not support robust tail-latency or universal-ranking claims.

The hashes and executed evaluator process improve reproducibility. They cannot prove that a human truthfully declared generation settings, that an arbitrary evaluator is adequate, or that the generated backend is production-ready. Preserve those limits beside any claim.
