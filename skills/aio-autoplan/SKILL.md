---
name: aio-autoplan
description: "Automatically refine and independently review an executable backend plan, with scope and developer-interface checks before engineering review. Use for autoplan or automatic backend planning; return to an authorized build controller without starting another pipeline."
---

# AIO Autoplan

Produce a ready backend plan from the accepted task. This adapts gstack's ordered planning orchestration: settle scope, check affected developer interfaces, then review engineering last. Standalone Autoplan delivers planning artifacts; an authorized Complete Destruction run continues implementation after the gates pass.

Inherit the [resource contract](../all-in-one/references/resource-budgets.md), original journal and source authority. Standalone runs resolve thorough once. Select only relevant stages; Autoplan is a planning coordinator inside the current run, not another end-to-end controller. Do not launch separate reviewers for each planning lens or mandatory outside-model voices.

## Protocol

1. Bind the exact accepted task, repository and current changes. Reuse an existing matching contract/plan. Identify materially missing facts and continue independent planning while obtaining them. Accepted implementation authority persists through planning; a planning request alone does not authorize a build.
2. Resolve the [scope mode](../aio-brainstorm/references/modes.md). Default **HOLD SCOPE**. Use Brainstorm only for unresolved outcomes or alternatives. **SCOPE EXPANSION**, **SELECTIVE EXPANSION** and **SCOPE REDUCTION** control proposals; additions or deferrals outside the accepted task need a scope decision before entering R/U/V records. Settled requirements remain binding.
3. Use [AIO Spec](../aio-spec/SKILL.md), [Architecture](../aio-architecture/SKILL.md) and [Plan](../aio-plan/SKILL.md) for missing contracts, critical failure traces, exact interfaces, owned units and verification. A bounded prototype is conditional on a consequential uncertainty; it consumes the same journal and cannot be mistaken for production proof.
4. For an affected public API, SDK, CLI or operator integration path, apply [Devex Review](../aio-devex-review/SKILL.md) to the proposed developer journey before final engineering review. Default **DX POLISH**. Planned examples and inferred friction are planning evidence; unavailable runtime behavior stays untested. Findings become explicit plan amendments, not a new implementation run.
5. Freeze the final candidate and run the structural plan gate. Then reserve one independent `PLAN` reviewer through [Plan Review](../aio-plan-review/SKILL.md), covering scope/requirement consistency, relevant developer-interface findings, feasibility and adversarial failure handling. **Engineering review is last**: a subsequent material amendment invalidates affected readiness and needs a bounded scoped re-review. Reuse a matching current-source review instead of repeating it.
6. Resolve confirmed plan blockers in the shared corrective-wave allowance. Never reset caps or create independent per-lens retries. If required review, facts or remaining capacity are unavailable, retain a resumable blocked plan with the exact next action. Structural validity alone cannot mark it ready.

## Return and handoff

Return the human plan, machine index, R/U/V coverage, selected scope/DX modes, actual amendments, gate results and separate independent feasibility/adversarial verdicts. Unchosen opportunities remain a short optional list outside accepted scope. Avoid duplicate full reports for each lens.

Use the [stage contract](../all-in-one/references/stage-contracts.md). Return readiness to the caller. Under an authorized build, the existing controller continues with [AIO Work](../aio-work/SKILL.md); a standalone planning invocation ends with its reviewable plan.
