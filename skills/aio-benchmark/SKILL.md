---
name: aio-benchmark
description: "Run a fair, predeclared backend comparison of two or three workflows chosen from All in One, Compound Engineering and Superpowers using the same task, model settings and evaluator. Use when evidence is needed for a scoped quality or performance claim."
---

# AIO Benchmark

Compare actual backend artifacts under one fixed protocol. A single local task can support a claim about that task and its observed runs; it cannot establish that one plugin is universally best.

Declare the workflows requested for the comparison. The starter compares All in One and Compound Engineering; Superpowers is optional. Use two or three unique supported condition IDs and collect every trial for each declared condition.

Read [the protocol and schemas](references/protocol.md) before a comparison. Establish the backend task, correctness/security/recovery assertions, evaluator, trials, metrics, and common model/tool/runtime settings before generating condition outputs. Use [the definition starter](templates/definition.json) to record these choices; its draft status cannot be frozen.

Freeze the definition with the bundled standard-library runner. Give each condition a fresh equivalent workspace, the same task, the same relevant context budget and allowed tools, and the fixed settings. Apply only that condition's requested workflow. Record actual generation settings, elapsed time and limitations separately; this runner does not launch or attest hosted models.

Before freezing a persistence evaluator, exercise its fixture setup and cleanup independently of candidate code. If a harness defect is discovered later, preserve the original inputs and failure, verify the correction independently, and start a new freeze. Assessing already-generated artifacts with the correction is diagnostic evidence; label the changed chronology and do not call it a blind comparison.

```text
python "<skill-dir>/scripts/benchmark.py" freeze definition.json --root workspace --output frozen.json
python "<skill-dir>/scripts/benchmark.py" collect frozen.json --root workspace --condition aio --trial trial-1 --artifact aio.py --output aio-trial-1.json -- python evaluator.py aio.py
python "<skill-dir>/scripts/benchmark.py" compare frozen.json --root workspace --output comparison.json --results aio-trial-1.json ce-trial-1.json
```

The evaluator executable and arguments after `--` come directly from the caller. The frozen evaluator file must be among those arguments. Commands embedded in definition or result JSON are never executed. Run unfamiliar evaluators only within the task's existing authority and isolated resources.

Collect every declared condition/trial, including failed, timed-out, or malformed evaluator runs. Do not replace weak runs silently, change the evaluator after seeing outputs, or select a winning subset. A changed task, evaluator, metric, setting or trial set starts a new freeze and comparison. If a rerun is needed, retain the first outcome and declare a new complete trial for all conditions.

Correctness, security and recovery come first. A condition with any failed gate is ineligible for performance comparison. Inspect the evaluator assertions and raw artifacts independently; a syntactically valid result is not proof that its tests cover the intended backend behavior. Report full trial outcomes, sample count, evaluator wall time, declared metrics, hashes, and unmeasured dimensions. Keep conclusions within those observations.
