---
name: launch-readiness
description: "Run the final evidence-based readiness checkpoint for iOS App Store and Android Google Play submissions, including release quality, privacy policies, SDK data practices, store declarations, account deletion, permissions, conditional policy checks, and legal applicability. Use before mobile submission or to audit a rejected app."
---

# Mobile launch readiness

Inspect the actual mobile app, its backend, candidate build, SDKs and store metadata. Produce a verified readiness dossier and resolve authorized defects. A source scan or privacy-policy file alone cannot establish readiness.

## Intake and facts

Establish target platforms and storefronts, legal developer entity/contact, audience/ages, app purpose, data categories and recipients, retention/deletion, SDK/model providers, accounts, tracking, payments, user content, AI output and regulated uses. Inspect evidence rather than infer these from an empty template. Unknown material facts stay unverified.

Record exact source revision, bundle/package IDs, build versions and artifact digests. Inspect the live official sources in [policy sources](references/policy-sources.md) on every release audit; record the review date and current applicable rules. If browsing or necessary console/device access is unavailable, do useful local work and leave affected checks unverified.

## Specialist audits

For iOS, run the copied [Apple App Store reviewer](../apple-appstore-reviewer/SKILL.md). It reviews first and supplies findings; the integrating controller may then implement fixes already authorized.

For Android, run the copied [Google Play Policy Insights](../play-policy-insights/SKILL.md), including its bundled scripts and prompts. Inspect [Google audit integration](references/google-audit-integration.md) first. A failed upstream fact-gathering run is a blocked Google audit, not a successful manual substitute. Record its actual output and coverage: it addresses data safety, reviewer access and permissions, rather than every Play policy or legal obligation.

Reconcile these reports with [release checks](references/release-checks.md) and the app's features/markets. Run the required functional, backend, security and device/store tests. Mark each item pass, fail, unverified, or not applicable with evidence and a scope reason. An unavailable artifact is not automatically a violation, but it cannot support a ready verdict.

## Privacy and legal checkpoint

Build the [data inventory](templates/data-inventory.csv) from observed flows, including backend logs, model APIs, embeddings/memory, analytics and third-party SDKs. Reconcile implementation, public policy and store disclosure answers. Use [privacy and legal review](references/privacy-and-legal.md) and the [privacy draft scaffold](templates/privacy-policy.md) to prepare an accurate draft from actual facts. Do not promise no collection, immediate deletion or universal compliance unless those claims are evidenced and applicable.

Legal applicability depends on markets, audience and product. Obtain a qualified legal determination where the risk requires it; unresolved legal questions stay review needed. A developer's factual confirmation and any required counsel review cannot be fabricated by an agent. Terms, licenses, content rights and developer attestations are separate from code tests.

## Mechanical final gate

Fill [launch report](templates/launch-report.json) using the [report format](references/report-format.md) and actual evidence. Resolve paths relative to the app workspace and run:

```text
python "<skill-dir>/scripts/launch_gate.py" "<launch-report.json>" --root "<app-workspace>" --json
```

The starter is blocked. The gate requires release-wide and per-platform coverage, conditional feature checks, current-day policy evidence, source/build hashes and existing evidence artifacts. It does not execute recorded tests, validate legal conclusions, inspect a remote store, or certify an app. Do those observations separately.

For ready for submission, every applicable required check must pass with evidence, unknown material facts must be resolved, and blockers must be empty. Keep submission readiness separate from submitted, approved and released. Actually submitting or publishing requires the user's authorization and applicable account access.

Return the dossier, prioritized fixes, changed files, executed checks, verdict and exact limitations. Link the reports and build. Passing this checkpoint cannot guarantee store approval or eliminate future legal trouble.
