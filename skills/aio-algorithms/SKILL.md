---
name: aio-algorithms
description: "Build and verify backend algorithms with independent oracles and explicit resource bounds."
---

# AIO Algorithms

Build and verify backend algorithms with independent oracles and explicit resource bounds.

## Protocol

1. Read [algorithms](../all-in-one/references/algorithms.md). Specify inputs, outputs, invalid cases, ties, numeric/error tolerance and time/space dimensions.
2. Select the simplest suitable algorithm and derive its complexity, including database/network round trips. State the correctness invariant independently from implementation.
3. Construct a trusted bounded oracle or property checks and meaningful adversarial cases before optimization. Exercise empty/large/skewed input, duplicates, ties and overflow/precision boundaries where relevant.
4. Implement through [aio-tdd](../aio-tdd/SKILL.md); compare results against the oracle and measure representative memory/time. Concurrency or caching must preserve cancellation, invalidation and ordering semantics.
5. Return exact workload/results and limits. Benchmark anecdotes do not establish universal speed improvements.

## Return and handoff

An algorithm implementation with oracle/property evidence, complexity and representative measurements.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
