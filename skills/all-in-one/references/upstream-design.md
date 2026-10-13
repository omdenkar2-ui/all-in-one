# Upstream design and backend synthesis

This release studies locally installed Compound Engineering **3.27.0**, Superpowers **6.4.2**, and gstack's installed skill files. CE/Superpowers versions are observed package versions, not inferred Git revisions. gstack's release version and Git revision are unavailable; its local file digests identify the inspected snapshot. The packaged source registry records the inspected files/hashes; use those records when reproducing the research. Backend domain source pins live in [sources.json](../knowledge/sources.json).

All in One's AIO procedures are an original synthesis. Two separately identified mobile-launch specialists are vendored under their upstream licenses; they are not the source of the backend controller design.

## Source feature to implemented contract

| Inspected source feature | AIO implementation | Backend consequence |
| --- | --- | --- |
| CE LFG's accepted source and continuous stage orchestration | Complete Destruction plus shared stage input/return contracts | One controller preserves scope, run identity and destination while specialists return evidence |
| CE brainstorming's proportional scope and outcome framing | AIO Ideate/Brainstorm, bounded brief and recorded alternatives | Agent frameworks and infrastructure choices remain means; requirements express caller/operator outcomes |
| CE planning's maintained work source, settled decisions and stable units | AIO Spec/Plan/Plan Review with R/U/V/D coverage | Workers implement the exact source rather than inventing acceptance or reopening chosen tradeoffs |
| CE work's integrated ownership and recoverable progress | AIO Work, source-bound execution ledger, Handoff/Resume | Current files, untracked changes and observed effects govern resumption; successful effects are reconciled rather than replayed |
| CE review, diagnosis, simplification and reusable learning | AIO Review/Debug/Simplify/Compound | Findings require concrete consequences, repairs address causes, and lessons preserve reasoning absent from code/tests |
| CE delivery and PR follow-through | AIO Commit/Ship/CI/Feedback/Release | Owned changes, exact-head checks and actual destination state are distinct observed claims |
| Superpowers' intent-first design and isolated responsibilities | AIO Brainstorm/Architecture and explicit unit inputs/outputs | A worker can understand its interface without reconstructing unrelated internals |
| Superpowers' concrete plans and independently testable task boundaries | AIO Plan's exact files/signatures/assertions, dependencies and ownership | Each unit carries a meaningful acceptance cycle; vague “handle errors” steps do not settle a contract |
| Superpowers' observed test-first work | AIO TDD/Test and worker red/green reports | Tests must fail for the absent/wrong behavior before the production change; missing historical evidence stays missing |
| Superpowers' spec-before-quality review and fresh workers | AIO Work's ordered spec/risk reviews and minimal unit packets | Compliance is established before broader risk review; worker success cannot close a controller checkpoint |
| Superpowers' systematic debugging | AIO Debug's reproduction, boundary trace and falsifiable hypotheses | Failed recovery or tenant checks are diagnosed without speculative patches or nested retries |
| Superpowers' verification before completion | AIO Verify/Proof/Checkpoint and final receipt | Assertions need fresh integrated evidence, and recorded JSON cannot authenticate tests or publication |
| gstack engineering review's failure-mode/test map | AIO Plan Review's handling, test and observability ledger | Silent unhandled failures become explicit plan gaps |
| gstack functional QA across APIs, CLIs, workers and webhooks | AIO Test's contract-to-probe evidence | Acceptance/enqueue is distinguished from final durable business effect |
| gstack CSO's agent/MCP/skill-supply-chain traces | AIO Security's conditional trust-boundary procedures | Plugins, prompts, memory and tool configuration are reviewed for consequential authority paths |
| gstack test-value and developer-experience audits | AIO Test Audit and AIO Devex Review | Existing regression value is preserved; actual developer flows are tested rather than scored from claims |
| gstack health's checker exit/log discipline | AIO Verify's bounded local check runner | A wrapper/tail cannot turn failed or incomplete checker execution into a pass |
| gstack canary's fresh observations and identified baseline | AIO Canary's backend adaptation | Deployment revision, signals, service thresholds and durable outcomes govern a bounded observation |

For consequential architecture, AIO adds concrete backend contracts around these procedures: typed state and reducers, model proposal versus executor authority, trusted tenant context, durable business-operation identity, crash-after-effect reconciliation, retry/budget ownership, terminal uncertainty states and versioned schema/history compatibility. These contracts route to domain playbooks and actual failure tests.

## Deliberate conflict resolutions

**Authority follows the user and host.** Superpowers' staged human-approval workflow is useful reference data, but All in One preserves the user's explicit authorization for autonomous completion. A standalone planning request stays planning; an accepted build continues through routine phases. New irreversible scope or missing material facts remain actual dependencies.

**One pipeline owns delivery.** CE and Superpowers offer complete workflows; AIO does not nest their controllers or start shipping from each leaf. Source plugins are not runtime dependencies. In a pipeline, AIO Work returns owned implementation evidence; the integrating controller owns final verification, review, delivery and close-out.

**Test-first evidence is proportional and honest.** Changed behavior requires meaningful red/green observations. A mechanical nonbehavioral change or bounded spike uses an explicit suitable check instead of a fabricated failing test. An inherited passing implementation does not gain retroactive TDD history from a new green run.

**Review readiness differs from structural readiness.** The plan gate can accept a coherent structural candidate before independent semantic review. Its stage/ledger remains blocked for execution until required review and binding findings are settled. Implementation checks may pass before delivery; full completion is checked only after the requested destination is observed.

**Backend contracts drive coverage.** API, effect, data, workflow and algorithm invariants select the tests. No fixed checklist certifies every backend, and no frontend workflow is added. Optional mobile release auditing remains a separate requested stage.

**New specialist lenses share the run budget.** gstack's browser/design procedures, repeated general preambles, runtime startup/telemetry and automatic outside-model calls are not bundled. Its browser canary is adapted to backend signals; this is not a claim that its browser implementation provides backend metrics. AIO's original admission estimator preserves closing capacity, and affected-mechanism routing avoids duplicate reviews. None of these instructions establishes a hard provider token/billing cap.

## Gstack-style mode selection in 1.5.0

The [mode directory](modes.md) preserves meaningful installed gstack names while separating scope and evidence selection from AIO's resource profiles. Autoplan retains scope/developer-interface-before-engineering ordering, with engineering last and one independent PLAN job. AIO defaults to HOLD SCOPE rather than gstack Autoplan's SELECTIVE EXPANSION: accepted backend work should not acquire automatic product additions. Full/Quick/Regression QA and Quick/Standard/Exhaustive repairs remain distinct; QA Only is report-only. Existing DX, security, canary and health stages use short conditional references rather than duplicated controllers.

Careful/Freeze/Guard are agent scope procedures without native host hooks. AIO comprehensive security means authorized controlled reproduction, not gstack's qualified runtime catalog, private launcher, signed witness or replay tooling. Source runtime scripts and shared startup/telemetry blocks are not copied. Required checks, trusted user scope and original budgets remain binding in every mode. These adaptations describe procedural capabilities, not a completed quality or token-cost comparison against gstack.

## What this matrix does not establish

Adopting a procedure is not proof of higher-quality generated applications. All in One is newer and has less operational history than its reference workflows. More specialist entrypoints may improve selection but also add maintenance and context costs. Independent reviews and evaluator quality still depend on actual host capabilities and source evidence.

The bundled helpers reject inconsistent structure, unsafe paths and selected stale/missing evidence; they do not authenticate human declarations, test execution or provider behavior. Model-generated fixtures, mocked dependencies and synthetic fault injection need explicit limits. Production integrations and store release facts require their own observations.

Use [AIO Benchmark](../../aio-benchmark/SKILL.md) to compare actual artifacts under a frozen backend task, independent evaluator, common model/tool/runtime settings and retained trials. Evaluate correctness, tenant/security behavior and recovery before latency/cost. Report the task, sample size, generation limitations and raw failures alongside any scoped claim; package test counts do not establish superiority.
