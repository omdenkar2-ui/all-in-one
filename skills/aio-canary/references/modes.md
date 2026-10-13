# Backend canary operations

Resolve the accepted environment, deployed identity, boundaries, baseline and signal policy before querying. Explicit user requests govern. `--baseline` and `--quick` are alternative operations; do not silently turn capture into comparison or monitoring.

| Operation | Work and claim |
| --- | --- |
| `--baseline` | Capture the declared revision/configuration, cohort, timestamps, query windows, denominators, metric distributions and authorized functional evidence. Preserve the original baseline. Post-deploy capture is a monitoring-start reference, not proof of a pre-deploy baseline. Return capture quality and gaps rather than candidate-release health. |
| `--quick` | Perform one bounded pass of the selected signals and authorized probes. Report that pass against the configured comparable baseline and targets. Do not add wait/retry rounds to simulate a full observation window. |
| **normal**, default | Compare the candidate and available control/baseline over the accepted bounded window, cadence and maximum rounds within the original remaining deadline. With no selected window, perform one pass and label it a single-pass observation; do not invent a monitoring duration. |

`--duration <duration>` (for example `5m`) requests a positive bounded observation window, including query waits, within the original remaining deadline. Keep configured cadence and maximum rounds; do not infer recurring monitoring from this selector. An infeasible required window remains pending/inconclusive or blocked as applicable rather than extending the run. Quick still performs one pass and baseline still only captures; duration never changes their operation or minimum-evidence requirements.

Quick mode cannot waive the configured minimum window, sample counts, signal freshness, transient-confirmation rule or functional assertions. It can report **healthy** only if the existing evidence and this pass satisfy all required conditions for its declared scope, including a configured comparable baseline and comparison policy. Missing signals, baseline, thresholds, empty traffic, stale data or an incomplete minimum window are **inconclusive**, even when the health endpoint succeeds. A captured baseline alone cannot establish candidate health.

Use **breach** for an evidenced violation under the configured policy, retaining missing coverage separately. Use **pending** for owned operations still running and **blocked** for prerequisites that prevent observation. Keep stage status separate from operational verdict and state actual samples, elapsed window and assessed effects.

All operations share the original journal, caps and authorized actions. No mode deploys, changes traffic, overwrites a baseline or rolls back without existing authority. Do not launch extra reviewers, create recurring monitoring or persist notifications from a mode choice; recurring work requires an explicit request and available scheduler.
