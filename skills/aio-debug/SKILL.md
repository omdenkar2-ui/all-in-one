---
name: aio-debug
description: "Diagnose a backend bug, failed test, CI failure, agent/tool issue or pipeline incident by reproducing it, tracing boundaries and testing a causal hypothesis before a targeted fix. Use when behavior is unexplained or previous patches have not resolved it."
---

# AIO Debug

Preserve any requested [Careful / Freeze / Guard](../aio-work/references/scope-guards.md) modifier from the owning run. Diagnosis can inspect dependencies, but a repair cannot silently widen resolved edit ownership. These modifiers are agent procedures rather than native blocking hooks.

Find the causal mechanism before patching a symptom. Read [diagnostic procedure](references/diagnosis.md) and maintain the [hypothesis log](templates/hypothesis-log.md) for multi-step failures. Preserve current user work and any useful failing artifacts.

Capture the expected/actual behavior, triggering inputs, source/build/environment identity and complete error. Reproduce with the narrowest trustworthy test or request. If reproduction is nondeterministic, collect traces and isolate the condition before guessing. Do not log secrets, prompt contents with personal data, or production records wholesale.

Trace the first incorrect value/state across relevant API, agent, queue, storage and provider boundaries. Compare a working case and recent changes. State one falsifiable hypothesis supported by the evidence, then run the smallest discriminating experiment. Change one causal variable at a time.

After confirming the hypothesis, establish a regression test/red failure with [AIO TDD](../aio-tdd/SKILL.md), apply the bounded fix, then run the reproduction and affected contract/recovery tests. Use [AIO Review](../aio-review/SKILL.md) for consequential fixes and [AIO Verify](../aio-verify/SKILL.md) before claiming resolution.

After three ineffective fixes, stop repeating the same approach: preserve attempts, revisit assumptions/state ownership/transaction ordering, obtain fresh review where available, and change the hypothesis or architecture within scope. Required behavior remains blocked until proved. Continue independent safe work and return the exact unresolved condition and next diagnostic action.

A diagnostic-only request ends with evidence and cause/uncertainty. A repair request or enclosing implementation controller carries the verified fix back to its checkpoint; this skill does not start a competing shipping pipeline or publish an incident response without authorization.
