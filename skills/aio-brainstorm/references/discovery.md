# Backend discovery

Use the smallest investigation that can settle the next consequential decision. Existing code, tests, contracts and the user's explicit choices outrank an attractive new stack.

## Define the work rather than its branding

Follow one concrete request or event from its producer to the result that matters. Who can initiate it? Who can see the result? What constitutes completion? Identify data ownership and operations with external effects. For “an autonomous agent,” discover which decisions may be model proposals and which actions need enforced authorization. For “a pipeline,” discover source partitions, dependencies, freshness and what must survive restart.

Split independently valuable outcomes into bounded delivery slices without losing requested coverage. A named provider is not automatically a new subsystem: determine whether an existing abstraction already satisfies it. Keep critical integration and recovery behavior inside the slice that owns the result.

## Compare meaningful alternatives

Use the same workload and contract for each option. A useful comparison includes the existing implementation, a minimal modification and an alternative only where it changes an important tradeoff. Compare latency and cost, persistence, replay, operator burden, isolation and reversibility. Attribute facts to inspected code or current official documentation; label estimates and assumptions.

Example: a short authenticated request can stay synchronous; a queue fits detached work; a durable coordinator may be justified by several external operations and long waits. The deciding question is whether a crash can violate the required result, not whether a framework supports agents.

## Expose decisions that change correctness

Determine these only where they affect the requested work:

- Success, partial success, cancellation and terminal failure as observable states.
- Duplicate requests, timeouts after successful writes and recovery after worker loss.
- Tenant and tool authority, data classes, retention and provider boundaries.
- Numeric deadlines, retry/concurrency limits, cost and resource bounds, or an explicit experiment to establish them.
- Existing schema/API compatibility and permitted rollout disruption.

Do not invent production targets. A provisional capacity estimate names its basis and validation task. A missing product fact becomes a question or blocker; a reversible implementation choice can be decided within existing authorization.

## Preserve decisions and contradictions

Record who supplied a constraint and its source. An agent preference is not a user decision. Preserve chosen alternatives and reasons so the next phase does not restart discovery. If observed evidence conflicts with an accepted constraint, distinguish workable drawbacks from infeasibility: retain the former with a tradeoff; report the latter with the evidence and a specific recovery choice.

The final brief should make unresolved decisions visible at their owning requirement. Rewrite superseded text in place; do not leave incompatible versions scattered across appendices. Mobile store audits and frontend design are outside this discovery path unless separately requested.
