---
name: all-in-one
description: "Route REA artifact investigations and backend development, APIs, agent architecture, workflows, data pipelines, algorithms, debugging, review and delivery to All in One's focused aio stages. Use for backend requests needing an appropriate engineering workflow; use complete-destruction for explicit autonomous end-to-end execution."
---

# All in One

Own the user's backend intent and choose the smallest suitable stage. The plugin contains 42 focused AIO skills, two controllers, seven compatibility entrypoints three optional mobile launch skills and REA artifact analysis. It supports APIs, agent systems, durable workflows, data and algorithms; frontend design and implementation are outside this suite.

Resolve the [resource contract](references/resource-budgets.md) once per run: thorough is the selected default, with inherited dispatch/time limits and soft token targets. Map affected mechanisms to required checks, estimate costly next work while preserving closing capacity, and consult only matching [catalog](references/skill-catalog.md) rows and selected entrypoints. Use the [shared stage contract](references/stage-contracts.md) for input/evidence rules. Source plugins inform these procedures; their whole-project pipelines are not recursive controllers.

Use the [mode directory](references/modes.md) only for requested or relevant selectors. Scope, QA depth, repair severity and guard choices remain separate from the resource profile; optional modes do not create more controllers or waive accepted checks.

## Route by intent

| Request | Stage |
| --- | --- |
| Supplied app, binary, package or requested runtime evidence | [REA](../reverse-engineer-anything/SKILL.md) |
| Unclear outcomes or alternatives | [AIO Brainstorm](../aio-brainstorm/SKILL.md); AIO Ideate for option generation |
| Behavior contract or architecture | [AIO Spec](../aio-spec/SKILL.md), [AIO Architecture](../aio-architecture/SKILL.md); AIO Prototype for a bounded uncertainty |
| Executable plan | [AIO Plan](../aio-plan/SKILL.md), then [AIO Plan Review](../aio-plan-review/SKILL.md) |
| Automatic planning with ordered scope, developer-interface and engineering checks | [AIO Autoplan](../aio-autoplan/SKILL.md) |
| Accepted implementation or named build plan | [AIO Work](../aio-work/SKILL.md) |
| One-prompt autonomous completion | [Complete Destruction](../complete-destruction/SKILL.md) |
| Unexplained failure | [AIO Debug](../aio-debug/SKILL.md) |
| Inspect, review or explain | [AIO Review](../aio-review/SKILL.md), AIO Doc Review or AIO Explain |
| Verify or deliver | [AIO Verify](../aio-verify/SKILL.md), [AIO Ship](../aio-ship/SKILL.md) |
| Saved run | [AIO Resume](../aio-resume/SKILL.md) |
| Compare generated output | [AIO Benchmark](../aio-benchmark/SKILL.md) |
| Audit test value or duplication | [AIO Test Audit](../aio-test-audit/SKILL.md) |
| Explore backend behavior and repair authorized defects | [AIO QA](../aio-qa/SKILL.md) |
| Functional QA report without applying fixes | [AIO QA Only](../aio-qa-only/SKILL.md) |
| Assess API/SDK/CLI integration experience | [AIO Devex Review](../aio-devex-review/SKILL.md) |
| Observe a deployed backend against its baseline | [AIO Canary](../aio-canary/SKILL.md) |

A supplied plan path alone does not authorize implementation. An explanation or report-only review ends with that requested artifact. Within an authorized build, planning returns to execution and does not end the run. Preserve the current stack, settled choices and user changes. Ask only for missing information or authority that materially blocks the task; existing authorization remains effective. Routine reversible edits need proportional checks.

REA is an optional investigation specialist, not another controller. Use it when the requested claim needs shipped-artifact or runtime evidence; ordinary source analysis stays with repository tools. In an authorized backend build, return its evidence to the current plan and controller. Read [REA integration](references/rea-integration.md) only for connection, runtime or release details.

## Select backend domain guidance

| Concern | Playbook | Focused implementation |
| --- | --- | --- |
| Services, interfaces, queues and reliability | [Architecture](references/architecture.md) | AIO Architecture / AIO API |
| Agent state, tools, budgets and checkpoints | [Agent workflows](references/agent-workflows.md) | AIO Agents |
| Jobs, DAGs, retries and backfills | [Pipelines](references/pipelines.md) | AIO Pipelines |
| Correctness, complexity and resource bounds | [Algorithms](references/algorithms.md) | AIO Algorithms / AIO Optimize |
| Transactions, indexes and migrations | [Data](references/data.md) | AIO Data |
| Permissions, tenants, secrets and injection | [Security](references/security.md) | AIO Security |
| Tests, reviews and receipts | [Verification](references/verification.md) | AIO TDD / Test / Verify |
| Local artifacts, PRs, CI and rollout | [Delivery](references/delivery.md) | AIO Ship / CI / Release |
| Reproduction and causal diagnosis | [Debugging](references/debugging.md) | AIO Debug |

Delegate meaningful independent units, not one worker per file, with explicit ownership and interfaces. One controller integrates actual changes, owns canonical commits and reserves journal events before dispatch or repair. Workers inherit the same budget and return scoped evidence. A fresh reviewer may perform spec then risk in one job with separate verdicts, stopping at a spec blocker; final review requires whole-change coverage. Reuse matching current-source evidence. Test changed behavior with observed failing proof. Budget exhaustion preserves unresolved work; it cannot make an incomplete gate pass.

## Search the backend knowledge base

Resolve paths from this skill directory. Python 3.10+ is needed only for helpers; procedures remain readable without it.

```text
python "<skill-dir>/scripts/knowledge.py" search "idempotency recovery" --json
python "<skill-dir>/scripts/knowledge.py" search "tenant" --domain security
python "<skill-dir>/scripts/knowledge.py" sources --json
python "<skill-dir>/scripts/knowledge.py" check
```

Canonical JSON and source pins live in `knowledge/`; the SQLite index provides offline search. Inspect installed versions or official current documentation for version-sensitive claims. After canonical records change, run `knowledge.py build --force` then `check`. Pins identify inspected snapshots, not the newest release.

## Gate plans and completion

For substantial execution, use the [AIO Plan JSON index](../aio-plan/templates/plan.json) and its [schema](../aio-plan/references/plan-schema.md), then run the structural gate before independent semantic plan review:

```text
python "<skill-dir>/scripts/plan_gate.py" plan.json --root workspace --json
python "<skill-dir>/scripts/check_receipt.py" receipt.json --root workspace --json
```

The [receipt starter](templates/evidence-receipt.json) is blocked. Implementation verification checks acceptance before delivery; completion verification adds observed delivery and the final receipt afterward. Helpers reject inconsistent structure, hashes and coverage; they do not authenticate command execution, test adequacy, publication or legal compliance. The controller performs actual checks and inspects destination state. Unavailable independent review or unmet acceptance remains visible and blocks a corresponding complete claim.

Use [Launch Readiness](../launch-readiness/SKILL.md) only for a requested mobile release. Store approval and future legal outcomes are not guarantees these skills can issue.
