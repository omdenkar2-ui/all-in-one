# Launch evidence report format

Start from templates/launch-report.json and keep the exact schema fields. The starter deliberately cannot pass. Store evidence under the actual app workspace; all file paths are relative to that root without traversal. Keep credentials and private user data out of artifacts.

| Field | Required content |
| --- | --- |
| schema_version | Integer 1 |
| verdict | ready_for_submission, blocked, or review_needed; only ready passes |
| source | path and SHA-256 of the authoritative acceptance/source-revision record |
| app | name, real developer_entity, unique platforms (ios/android), markets, features |
| policy_review | checked_on (actual audit day), sources (official HTTPS URLs), evidence files |
| builds | One platform/path/sha256 entry per platform for the candidate .ipa/.zip or .aab/.apk |
| checks | Unique id/status/evidence entries; reason for nonpass; optional command/exit_code |
| blockers | Explicit unresolved blockers; must be empty to pass |

The source record should identify the actual repository revision and any uncommitted changes included in the candidate. Its digest establishes the record's identity; it does not independently prove provenance of the build. Preserve build tooling/signing/device evidence for that relationship. Candidate digests identify the files tested; the checker does not inspect their executable contents or signatures.

Every feature is an established boolean: backend, accounts, tracking, payments, ugc, children, regulated_data, ai_generated_content. Unknown applicability stays unresolved and cannot establish readiness. Markets and developer identity must reflect actual facts, not fixture values.

Each check has a status of pass, fail, unverified, or not_applicable. Pass requires existing evidence files. Nonpass requires a reason. A recorded passed command requires integer exit_code 0. Human/console/legal observations may omit command and exit_code and use a dated factual report instead. Every failed or unverified check blocks; required checks cannot be waived as not applicable.

## Required check identifiers

Common: release-build, core-flows, privacy-policy, data-inventory, permissions, security, store-metadata, review-access, legal-applicability.

iOS: ios-review, ios-privacy, ios-release.

Android: android-google-audit, android-data-safety, android-release, android-testing. android-testing includes evidence of account-specific applicable console/testing requirements or their established nonapplicability within that passed scope check.

Enabled features add: backend-live, account-deletion, tracking, payments, ugc, children, regulated-data, ai-content. Accounts also add ios-account-deletion and/or android-web-deletion for the selected platforms. Further checks required by the actual contract/policies belong in the report too; the fixed matrix is a minimum grouping, not every possible obligation.

Policy sources must include the current Apple review guidelines and App privacy details for iOS; Google's User Data and Data safety pages for Android; Google's account deletion page when Android accounts apply. Consult policy-sources.md for URLs and additional applicable pages. Keep observed excerpts/findings in policy_review.evidence and check the current live sources. A date or URL in JSON cannot authenticate that observation.

Run launch_gate.py with --root and --json. --as-of is only for the actual audit day when the host date/timezone differs. Never backdate it to accept stale evidence. --requirements prints the required matrix and makes no readiness claim.

The checker is read only and works locally using the bundled core evidence validator. Keep the full plugin together when relocating it. It does not run tests, browse, confirm policy truth, certify legal advice, or establish store approval. The controller remains responsible for actual observations and truthful evidence.
