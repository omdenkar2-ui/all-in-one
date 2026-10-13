# Backend QA modes

Resolve exploration and repair tier separately. The selected profile, original journal, accepted requirements, required checks and user authority remain binding. Read only the relevant functional contract, not every domain playbook. These prompt selectors are instructions to the skill, not executable CLI commands.

## Exploration

| Mode | Selected probes | Evidence limits |
| --- | --- | --- |
| **Full** (default) | Every applicable contract of the selected backend surface, including its relevant failure/recovery boundaries | Full describes declared scope, not every service or file in the repository. Bound probe count/time to the remaining run; incomplete required coverage stays blocked. |
| **Quick** / `--quick` | The success path and highest-risk changed edge, plus all accepted required checks | List other exploratory boundaries as not run. A quick smoke test cannot establish full acceptance, tenant isolation or recovery when those remain untested. |
| **Regression** / `--regression <previous-report>` | Applicable previous failures replayed against the documented expected contract, then changed adjacent behavior and required checks | Bind prior report/input/environment to current scope. Distinguish fixed, still failing, new and not replayable. Keep the prior failure evidence intact. |

`--quick` also chooses the Quick fix tier. `--exhaustive` changes only the fix tier; it does not expand exploration. `--regression` preserves the chosen/default fix tier. If `--quick` and `--regression` are both supplied without a clear overriding exploration choice, preserve the explicit fix tier (or Quick tier when none overrides it), mark exploration unresolved and obtain the choice before running dependent probes. Do not guess a blended mode or ask again when the user already resolved it.

`--quick --exhaustive` selects Quick exploration and Exhaustive repair tier, regardless of flag order. Explicit Exhaustive tier also persists while resolving a Quick/Regression exploration conflict. QA Only still treats every repair tier as inapplicable.

## Fix tiers

| Tier | Authorized repairs |
| --- | --- |
| **Quick** | Critical/high confirmed defects in the selected scope |
| **Standard** (default) | Critical/high/medium confirmed defects in the selected scope |
| **Exhaustive** / `--exhaustive` | Also low-severity backend defects in the selected scope, only while budget and authorization permit |

Judge severity from consequence, reachable conditions and evidence, not a guessed score. Exhaustive adds no frontend or cosmetic work. A fix tier never grants implementation authority to a report-only request, silently defers accepted requirements, raises dispatch caps or creates fresh retries. A required blocker outside the tier remains unresolved until the scope/tier is legitimately reconciled; final acceptance cannot be green.

**QA Only** is orthogonal: use the same exploration modes but perform no code repairs, dependency/configuration changes, commits or shipment. Ignore fix tiers for execution and label them inapplicable. Safe test fixtures and report artifacts are allowed in owned disposable locations. Any probe that writes state must use an authorized isolated target and cleanup; observing production does not grant permission to mutate it.

## Compact report

Record run/source identity, exploration, repair tier or report-only policy, selected surface/contract, required R/V coverage, fixture and provider applicability, exact expected/actual outcomes, logs, findings and untested gaps. Use stable finding IDs for replays; preserve original failures rather than replacing the report with only successful retests. No universal QA score or readiness percentage is necessary.
