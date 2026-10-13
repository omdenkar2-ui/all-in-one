---
name: aio-test-audit
description: "Audit the value of existing backend tests with a bounded shortlist, actual callers and regression evidence. Use for test-suite cleanup or confidence gaps; report-only unless test changes are authorized."
---

# AIO Test Audit

Find tests whose maintenance cost exceeds the independent behavior they protect. Optimize confidence, not a deletion count; no justified candidates is a valid result. Use [AIO Test](../aio-test/SKILL.md) for designing new coverage.

Inherit the [stage contract](../all-in-one/references/stage-contracts.md), controller journal and [resource budget](../all-in-one/references/resource-budgets.md). A standalone audit resolves thorough by default. Reuse evidence only for the same accepted source, code/config/dependency snapshot, checks, environment and audited scope, including uncommitted/untracked files. This lens can share an existing review dispatch; it does not require another independent reviewer. Respect the remaining run capacity and checkpoint unfinished work without weakening required review or acceptance gates.

## Bounded discovery

1. Bind the requested paths or revision range and current snapshot. Inspect the declared runner, existing duration/flakiness data and retained coverage. Prefer changed or costly owner boundaries when the request permits sampling; disclose the chosen scope rather than claim a repository sweep.
2. Inventory in-scope test files mechanically before reading them. Use available `rtk`-prefixed file searches, runner inventory or duplicate detection to shortlist assertion-free probes, self-comparisons, source/export inventories, duplicate cases and test-only seams. Assertions hidden in helpers, protocol goldens and architecture guards can make these false positives. Respect explicit retention reasons and record them.
3. Default to at most 10 ready recommendations, 30 relevant file reads and 30 reference searches, all within the controller's remaining time/token budget. User limits take precedence. Record discovered, shortlisted, inspected, retained, unresolved and unread counts. A mechanical match is a lead, never a deletion verdict.

## Prove each recommendation

Read the complete candidate, its production owner, actual non-test callers and overlapping coverage. Follow package exports, registration/configuration, generated interfaces and dynamic dispatch where present; a text search with no hits cannot prove code is unused. Inspect relevant history for the regression or contract the test was added to protect.

For each candidate record its path/test ID, owner boundary, observable contract, credible regression, production callers and search limitations, stronger existing coverage, history, proposed action and validation command. Choose **retain**, **rewrite at the real boundary**, **extend existing coverage**, or **retire**. Incomplete proof remains unresolved. Static, slow or refactor-sensitive tests may still independently enforce public API, wire format, migration, tenant/security, ordering, package or release contracts; retain that protection.

Explain why stronger coverage would detect the same regression with an independent oracle. Matching assertions or green suites alone do not establish redundancy. If demonstrating a regression is authorized, use an isolated disposable experiment and confirm failure in the intended assertion. A claimed bug regression must fail before repair and pass afterward; collection, fixture or environment failures are not that proof. Record any relevant base control and its limitations.

## Authorized changes and return

Discovery is report-only unless the accepted task authorizes test changes. Within that authority, group supported edits by owner boundary, preserve the contract in the retained or replacement test, and run affected owner/integration checks. Do not edit while its runner is active. Production seam removal additionally requires production-change authority and export/caller analysis plus an appropriate build/typecheck or dead-code check; grep alone never justifies it. Reuse valid unchanged checks and reserve repairs/re-review through the existing controller.

Return a compact report with scope/snapshot, limits and counts, recommendation evidence, retained false positives, unresolved gaps, actual commands/results and the next bounded action. Separate proposed from applied changes and observed from estimated runtime/LOC savings. An audit complete for its declared scope does not certify whole-suite acceptance or authorize shipping.
