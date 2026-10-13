# Delivery, deployment, and learning

Match delivery to the user's requested destination. Local work can finish with verified files and a clear report. A PR requires an actual published PR; production delivery requires an authorized deployment and appropriate operational checks.

Inspect repository status before staging. Preserve user changes and stage only owned files. One integrator owns canonical commits; workers do not race to commit shared state. Follow repository checks and message conventions. Without a remote, complete local delivery without inventing a push, PR, or CI result.

For a PR, describe the concrete trigger and resulting behavior, the failure/compatibility tradeoff, and actual validation. Attach the created PR using the host's artifact tool when available. Check CI results on the relevant revision; a watcher starting or a stale green run does not satisfy the gate.

## Rollout and recovery

Before an authorized rollout, identify the target environment, exact artifact/revision, schema compatibility, secrets/configuration, health checks, and rollback criteria. Prefer a reversible sequence when possible. Do not infer production authorization from permission to edit local code.

Deployments that include schema or workflow changes may need mixed-version compatibility. Complete expand/backfill stages before destructive contraction, and keep workflow history compatible for active runs. Rollback may require forward recovery if data has changed; document that mechanism.

Verify service health and meaningful operations after rollout. Watch errors, latency, queue age, retries, and dependency capacity over a window suitable for the system. Claim only the checks actually performed. If rollout fails, preserve diagnostic evidence and perform the authorized recovery step.

## Evidence and reusable learning

The final report states deliverable, location, checks/results, and unresolved limits. Include commands or links sufficient to inspect evidence, without exposing secrets. A backend knowledge record guides implementation; it does not execute a live backend or certify reliability.

Capture a reusable lesson when it prevents recurrence and is not already explained by tests or code. Include symptom, boundary, root cause, correction, verification, and the conditions where it applies. Keep lessons searchable and source-backed. Update canonical knowledge JSON first, then rebuild/check SQLite.

Keep recoverable evidence until delivery is verified. Cleanup only known task-owned paths. A local install should be checked with the native plugin registry and by exercising its bundled helpers; catalog refresh may require a new chat or application restart, which should not be forced automatically.

## Focused execution stages

Use [AIO Canary](../../aio-canary/SKILL.md) for requested bounded backend deployment observation with identified baselines, fresh signals and configured thresholds. Missing observations remain incomplete; the skill does not grant rollout/rollback authority.
