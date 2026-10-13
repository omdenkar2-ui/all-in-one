---
name: aio-ship
description: "Deliver a verified backend change locally, through a requested PR, or to an authorized deployment target. Use for shipping after implementation/review or refreshing a PR description; follows exact-head CI and reports pending or blocked states truthfully."
---

# AIO Ship

Deliver to the destination the user actually requested. Read [delivery procedure](references/delivery.md). Shipping does not itself authorize merge, public release, destructive migration, or unrelated external messages. Preserve standing authorization and avoid repeated approval gates.

Resolve delivery mode from the accepted request: local artifact, PR, or an explicitly authorized deployment. For implementation delivery, verify the exact source and required review/check evidence with [AIO Verify](../aio-verify/SKILL.md) in implementation scope. Delivery may honestly be pending at this preflight. Once the requested destination is observed, completion scope can check the final receipt; an outer controller retains that final gate when present. A description-only request uses the actual diff and available evidence without claiming checks that have not run. Prepare a concrete build, scoped diff and reviewer-ready description before any genuinely required final authorization.

- **Local:** verify artifact presence, content/hash and reproducibility when relevant. Record paths and limitations. No remote configured means truthful local delivery, never an invented PR or failed attempt to publish elsewhere.
- **PR:** use [AIO Commit](../aio-commit/SKILL.md) for canonical owned changes; inspect actual repository/head/base/remote and matching PR presence. Create only when requested/inherited shipping intent authorizes it. After successful creation, attach the PR with the host artifact tool. Use [AIO CI](../aio-ci/SKILL.md) for exact-head required checks and feedback follow-through within the requested watch budget.
- **Deployment/release:** use [AIO Release](../aio-release/SKILL.md) for an authorized target, built artifact, configuration/migration/rollback prerequisites and observed health. Launch-store review applies only when mobile submission is in scope.
- **Description-only:** draft the title/body from the actual diff and evidence; edit the remote description only if requested. Do not commit/push because a PR URL was provided.

Return distinct observed states: local delivered, PR created with CI passed/pending/failed/attention, deployment healthy/failed/unknown, or blocked. A PR URL is not green CI; merge-ready is not merge authorization. When called by Complete Destruction, return delivery evidence and residuals to its single controller rather than rerunning implementation or closing its receipt independently.
