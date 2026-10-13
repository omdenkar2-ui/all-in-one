---
name: complete-destruction
description: "Complete authorized backend work autonomously from one prompt through requirements, agent architecture, gated plans, test-first units, independent reviews, recovery checks and observed delivery. Use for Complete Destruction or full end-to-end execution of backend systems, workflows, pipelines and algorithms."
---

# Complete Destruction

Carry the accepted backend task through verified delivery in one invocation. Keep working across units, checkpoint failures and recoverable interruptions. A plan or partial implementation is not the endpoint. The name does not expand authorization. Preserve the current stack, settled decisions and user work.

Own one controller and inherit the [resource contract](../all-in-one/references/resource-budgets.md), resolved once at intake with thorough as the selected default. Create a compact mechanism-to-check coverage map and preserve 20% of the soft target for required closing work. Consult matching [catalog](../all-in-one/references/skill-catalog.md) rows, applicable domain playbooks and the [stage contract](../all-in-one/references/stage-contracts.md); do not load every skill. Specialists return to this run and its budget, never to competing whole-project controllers.

## Establish work authority

Inspect the exact request or named source and repository. Record a stable run ID, accepted source path and SHA-256, requirements, binding decisions, requested destination, user changes and observable acceptance. For substantial work maintain the [checkpoint ledger](templates/checkpoints.md), exact plan index, unit packets and evidence in the repository's normal artifact location. Do not overwrite a named source with an unrelated newer plan.

Use [AIO Brainstorm](../aio-brainstorm/SKILL.md) only when outcomes or alternatives remain unclear. For coordinated substantial planning, [Autoplan](../aio-autoplan/SKILL.md) settles scope and affected developer interfaces before engineering review, within this controller and journal. Reuse its C1-C3 artifacts rather than replaying those stages. Continue independent work while requesting genuinely missing facts. Do not repeat approval gates for already authorized implementation. Frontend implementation is outside this mode; mobile readiness is an optional requested release checkpoint.

When the accepted task depends on a supplied app, binary, package or requested runtime behavior, use [REA](../reverse-engineer-anything/SKILL.md) as a scoped investigation specialist. Carry its observations, inferences and unknowns into C1/C2 and the current implementation plan, then continue this controller. Ordinary repository analysis does not require REA.

## Execute every applicable checkpoint

| ID | Required outcome | Stages |
| --- | --- | --- |
| C0 Intake | Exact source, scope, destination and current changes bound to the run | Controller; AIO Resume for a saved run |
| C1 Contract | Stable R requirements, interfaces, invariants and acceptance | [AIO Spec](../aio-spec/SKILL.md); Brainstorm / Ideate as needed |
| C2 Architecture | Service/agent state, authority, operation identity, budgets and failure recovery settled | [AIO Architecture](../aio-architecture/SKILL.md); bounded Prototype if needed |
| C3 Plan readiness | R/U/V coverage, owned files, dependency DAG, failure handling/test/observability map; structural and independent semantic gates pass | [AIO Plan](../aio-plan/SKILL.md), [AIO Plan Review](../aio-plan-review/SKILL.md) |
| C4 Implementation | All owned units implemented, integrated and independently reviewed in spec then risk order | [AIO Work](../aio-work/SKILL.md); TDD, API, Agents, Pipelines, Data, Algorithms as relevant |
| C5 Integrated review | Cross-unit spec, correctness, security and recovery blockers resolved; simplification verified | [AIO Review](../aio-review/SKILL.md); Security / Simplify as relevant; [Devex Review](../aio-devex-review/SKILL.md) for affected developer interfaces |
| C6 Implementation evidence | Required local acceptance, actual API/job effects, fault, oracle and resource checks pass on current integrated source | [AIO Verify](../aio-verify/SKILL.md) in implementation scope; Test / Proof / Optimize as needed; [Test Audit](../aio-test-audit/SKILL.md) for demonstrated suite-value concerns |
| C7 Mobile launch | Requested mobile readiness assessed from actual build and declarations, or reasoned not applicable | [Launch Readiness](../launch-readiness/SKILL.md) |
| C8 Delivery | Requested local artifact, PR or authorized release observed; required current-head checks resolved | [AIO Ship](../aio-ship/SKILL.md); Commit / CI / Feedback / Release / Observe as applicable; [Canary](../aio-canary/SKILL.md) for a requested deployment observation |
| C9 Completion | Acceptance, reviews, delivery and final receipt consistent with current source | AIO Verify in completion scope; AIO Checkpoint |
| C10 Learning and close | Useful evidence-backed lesson or reasoned no new lesson; final deliverable and limitations reported | [AIO Compound](../aio-compound/SKILL.md); Handoff for remaining blockers |

For a trivial reversible nonbehavioral change, record why an elaborate contract/plan or behavioral test is unnecessary and perform suitable verification. Behavior-changing configuration still requires failing boundary evidence. No accepted requirement, meaningful required check or external destination can be waived as ceremony.

Checkpoints are outcomes, not separate mandatory model jobs. A small one-unit thorough task normally uses one plan reviewer for feasibility/adversarial lenses and one implementation reviewer for ordered spec/risk plus explicit whole-change coverage. Do not create one reviewer per file or lens.

Resolve requested [work modes](../all-in-one/references/modes.md) once. HOLD SCOPE is the planning default; QA exploration and repair tiers are separate from the resource profile. Use [AIO QA](../aio-qa/SKILL.md) for selected functional exploration/authorized repair, reusing Test/Verify evidence at C6. A request for [QA Only](../aio-qa-only/SKILL.md) remains report-only. Quick modes cannot waive accepted checks, security/recovery evidence or current-source review; each nested stage inherits spent counters, original deadline and closing reserve.

## Execute units and reuse valid evidence

Run plan_gate.py from the core skill against the actual workspace and source digest. Its pass establishes structural coherence; it does not replace semantic review or prove readiness. Hold the execution ledger blocked until both structural and independent semantic checks pass. Reopen affected decisions when new evidence invalidates an interface or requirement.

Check the inherited budget journal before work and reserve each implementer/reviewer job before dispatch. Fresh owned packets stay within the resource contract's launch-prompt limit and link raw source instead of full history. One integrator owns canonical changes; workers own disjoint files or ordered shared edits. Observe red, implement green, then refactor. One independent reviewer can run spec then risk on the same frozen snapshot with separate verdicts; stop risk if spec is blocked. Inspect actual changes and integrated checks before accepting reports.

AIO Work returns implementation artifacts and may already supply current-source integrated review and implementation verification. Reuse that evidence for C5/C6 after checking exact snapshot, scope and oracle coverage; do not dispatch identical final passes again. If evidence is stale, incomplete or checks only a unit, run the missing integrated stage. Domain/security reviews add a relevant lens, not an arbitrary extra checklist.

Pre-delivery verification is **implementation** scope: delivery remains pending without blocking its local verdict. After C8, **completion** scope checks the observed destination and runs the final receipt. Never require delivery evidence before preparing or shipping the deliverable.

## Repair and resume

Use [AIO Debug](../aio-debug/SKILL.md) for unexplained failures. Form a falsifiable cause, assess the estimated next work against remaining capacity, reserve a repair-wave event, repair, rerun affected checks and request bounded scoped re-review. At most two aggregate corrective waves are allowed per run; dispatch, elapsed and observed-usage limits may stop work sooner. Checkpoint the exact unresolved action when exhausted, without resetting counters or converting failures into acceptance. Keep independent authorized work moving only while its budget and prerequisites permit it.

Use AIO Handoff / Resume to reconcile the run with current source, uncommitted changes, checks and remote state. An existing controller receives the next checkpoint; resume does not recursively start another controller. Completed matching units are not repeated after context loss.

## Launch, delivery and closure

Ordinary backend work records C7 not applicable with a scope reason. A requested App Store/Play Store launch cannot waive the checkpoint merely because only backend code is available. Missing owner declarations, live/device evidence or policy applicability stays blocked or review needed. Prepare privacy and submission artifacts from real facts; store acceptance and future legal safety cannot be guaranteed.

Prepare concrete reviewable artifacts before requesting genuinely missing external authority. Delivery follows existing authorization. A local artifact, PR and deployed service are separate observed destinations; no remote or pending CI cannot be described as published or green. Attach every created PR to the host task using its supported attachment tool.

Populate the core completion receipt from actual observations and run check_receipt.py; mobile release also runs launch_gate.py. These helpers check consistency and file/hash presence, not execution, publication or legal compliance. Perform the actual checks separately.

Complete only when all accepted requirements, applicable checkpoints, required checks and observed delivery are satisfied and blockers resolved. Otherwise continue useful authorized work, save a resumable blocked state and report the precise remaining prerequisite. The end of a prompt or retry budget is not completion.
