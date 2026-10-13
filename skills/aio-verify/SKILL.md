---
name: aio-verify
description: "Verify backend acceptance and completion against fresh tests, source snapshots and delivery evidence. Use before closing or shipping backend work, checking completion claims, or reporting configured local health checks."
---

# AIO Verify

For implementation or completion scope, produce a requirements-to-evidence verdict for the actual integrated backend source. A test plan, log fragment, worker claim, or passed receipt schema is insufficient. Read [evidence selection](references/evidence.md) and use the [verification matrix](templates/verification-matrix.md).

Resolve verification scope from the caller: **implementation** verifies local acceptance and required review before delivery; **completion** additionally verifies the requested destination and final receipt after delivery. Pre-delivery implementation verification can pass with delivery explicitly pending. It cannot claim the full task complete. Standalone claims that the whole task is done use completion scope.

`--health` selects a report-only configured-check dashboard; follow [health mode](references/modes.md) and return its dashboard. The acceptance protocol below applies to implementation/completion. Explicit acceptance/completion requests retain their scope, with health results as scoped evidence. Every mode uses the caller's original journal and [resource budget](../all-in-one/references/resource-budgets.md); standalone work resolves thorough. Health mode applies no fixes and cannot establish full acceptance or a readiness score.

1. Bind the exact accepted source and implemented snapshot, including uncommitted/untracked owned files. Resolve required checks from the contract and repository instructions. Keep pre-existing failures and meaningful unavailable environments visible.
2. Map each requirement/invariant/failure to a check with a correctness oracle, expected result, environment, command and evidence path. Use [AIO Test](../aio-test/SKILL.md) for semantic test selection; inspect existing coverage before adding tests.
3. Run required checks, inspect complete output and terminal exit status, and record pass/fail/unverified/not-applicable with reasons. Tests still running remain pending. Unexpected skipped/xfail cases, partial suites, missing dependencies and infra failures cannot be reported as passes.
4. Compare the tested snapshot with current files. Rerun affected checks after production/test/config/migration changes and integration. Preserve valid unchanged evidence; do not repeat the entire suite without a reason.
5. Check review findings and the requested delivery separately. In implementation scope, record the pending destination without requiring it to exist yet. In completion scope, use [AIO CI](../aio-ci/SKILL.md) for remote delivery and inspect the exact current head/destination. Unit tests do not prove a deployed endpoint is healthy.
6. In completion scope for substantial implementation, populate the [core evidence receipt](../all-in-one/templates/evidence-receipt.json) from actual observations and run `scripts/check_receipt.py` from the [core skill](../all-in-one/SKILL.md) with the actual workspace root. In implementation scope, prepare the matrix/receipt as pending without requiring the final completion checker to pass. A valid receipt checks internal consistency and artifact presence; it does not authenticate test execution, coverage, legal compliance or publication.

For several explicitly configured local checks, [the bounded runner](references/check-runner.md) can keep logs on disk and return compact evidence paths. Use it when capture/timeout handling saves work; a single ordinary check can run directly. Preserve the caller's existing run budget and all required acceptance checks. Missing tools, exhausted time, incomplete capture or an exit-zero suite with inadequate assertions remain unverified; the helper does not bind source freshness or prove readiness.

Independent review unavailable, accepted behavior untested, required CI unknown, or requested delivery unobserved remains a blocker for the corresponding completion claim. Return the verification scope, snapshot, acceptance matrix, actual check results, remaining limitations and precise next action. A read-only verification request reports gaps without applying fixes or publishing.
