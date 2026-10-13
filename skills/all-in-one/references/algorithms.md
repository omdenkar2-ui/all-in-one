# Algorithms and performance

State the actual problem before selecting a technique: input domain, output, invariants, acceptable error, and objective. Name workload dimensions such as items n, edges m, tenants t, payload bytes b, concurrency c, and dependency round trips r.

## Correctness first

For nontrivial algorithms, construct a simple trusted oracle for small inputs. Compare the optimized result against brute force or a straightforward reference implementation using generated and adversarial cases. Test empty input, duplicates, ties, extreme values, invalid data, ordering assumptions, and deterministic tie-breaking.

For graphs, cover disconnected nodes, cycles, repeated edges, and deep paths. For numeric algorithms, define precision, rounding, overflow, and tolerance. For streaming algorithms, state what information is discarded and the resulting error bound. An algorithm is not correct because a benchmark completes.

Analyze both time and space. Distinguish total work from critical-path latency, and include database/API calls. A nominally linear routine issuing one query per item may be slower and more fragile than a batched implementation.

## Optimize from evidence

Record a baseline with representative distributions and realistic concurrency. Profile to identify the limiting cost: CPU, allocation, serialization, I/O, contention, or dependency latency. Change one limiting mechanism and rerun the same benchmark. Include warmup where relevant, repetitions, environment, dataset, and baseline revision.

Measure p50/p95 latency, throughput, memory, and error rate when they matter to the contract. A microbenchmark demonstrates its fixture, not production performance. Report uncertainty and avoid universal claims such as 'always faster'.

Examples of justified changes include replacing repeated membership scans with a set, batching independent database lookups, removing repeated serialization, using a heap for top-k when k is small, or replacing a full sort with selection when order is unnecessary. Each introduces memory, ordering, or implementation tradeoffs that tests must cover.

## Concurrency, caches, and overload

Asynchronous I/O helps waiting; it does not automatically speed CPU-bound code. Bound concurrent tasks and queues, propagate cancellation, and avoid nested pools that multiply concurrency. Python parallelism depends on runtime and workload; inspect the actual environment rather than assume threads accelerate CPU loops.

A cache needs a correctness key, tenant scope, freshness rule, eviction policy, and invalidation on writes. Test stampedes and stale values. Shared mutable memoization can leak data between tenants.

Confirm optimized results still match the oracle and that resource use meets the contract under skewed inputs. If measurements do not improve the intended metric, retain the simpler implementation or explain the tradeoff.
