# Backend debugging

Capture the failing request/job/run, expected invariant, observed result, dependency versions, and smallest reproducer. Save the relevant logs and state without secrets. Distinguish a permanent defect from environment setup, external outage, and flaky timing.

Trace one operation across validation, authorization, domain logic, transaction, queue, activity, and acknowledgement. Correlate request/job/workflow IDs. Inspect both successful and failing traces. A retry may hide the initial failure or duplicate an effect; inspect the whole attempt history.

Form a specific hypothesis and name the observation that would disprove it. Test the smallest intervention. Examples:
- A duplicate charge follows a crash between provider success and receipt persistence: reuse the operation key and reconcile before retry.
- A fan-in loses a branch update: inspect the reducer and scheduler merge semantics.
- Old workflow runs fail after deployment: replay stored history against the new worker version.
- Queue latency rises while throughput falls: inspect connection saturation, retry volume, lock waits, and backpressure.
- A query degrades at scale: inspect realistic plans/cardinality and round trips before adding indexes.

For a code defect, first make the reproducer fail on the current implementation. Fix the causal boundary, then prove the reproducer and relevant regressions pass. Do not swallow exceptions, weaken assertions, disable isolation, or relabel failures to achieve a green result.

After three ineffective patches, stop repeating the same assumption. Reproduce again, inspect competing hypotheses, and reassess architecture or ownership. Preserve evidence, work source, and a clear next action if progress depends on unavailable credentials or external state.

For data corruption, define the affected set before repair. Make the repair repeatable, verify invariants and counts, and retain a recovery path. Editing code alone does not repair existing invalid records. Report what was repaired and what remains unverified.
