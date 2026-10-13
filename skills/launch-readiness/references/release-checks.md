# Evidence for mobile submission readiness

Collect one candidate release dossier. Each pass points to an artifact and actual observed result; every not-applicable item explains the feature or platform scope. The launch gate's matrix groups these observations without proving their truth.

## Common checks

Verify a reproducible release candidate, source/build identity, signing/configuration, install and launch, critical flows, failure/offline handling, backend availability, tenant/security controls, privacy policy, data inventory, store declarations, permissions, store metadata, reviewer access, current policy review, and legal applicability.

Use the app's normal test tooling. Include meaningful unit/integration/recovery tests for backend behavior and platform/device evidence for the mobile experience. Static inspection cannot replace installation, purchases, deletion or reviewer-access testing. Capture commands, versions, outcomes and relevant artifacts without credentials.

Confirm policy/support/deletion links work from the release experience and without special developer access where public access is required. The published policy must identify the real operator and match the data inventory. A local Markdown draft does not satisfy a live-link check.

## iOS dossier

Inspect actual release configuration, entitlements, permission explanations and privacy manifests. Reconcile App Store privacy answers with the app and integrated partners. Test reviewer access, account deletion if accounts exist, and applicable purchase/restore/subscription flows. Review listing, age/content metadata and notes against the live Apple guidelines. Do not hardcode one payment rule across all storefronts and entitlements.

## Android dossier

Inspect manifests/dependencies and merged release configuration. Reconcile Data safety with actual client, SDK and backend behavior. Test applicable account deletion both from the app and the external web resource. Verify permissions and review access; include live Play Console notices, signing/package requirements, target SDK and account-specific testing requirements. The copied Google auditor provides partial static coverage; the dossier also needs runtime and console evidence.

## Conditional checks

| Feature | Additional evidence |
| --- | --- |
| Accounts | Account/data deletion and retention; iOS/Android paths as applicable |
| Tracking | Actual tracking/permission/consent behavior and declarations |
| Payments | Platform/storefront-appropriate billing, restore, subscription/cancellation and disclosures |
| UGC | Moderation, reporting, blocking, contact and actual handling |
| Children | Audience/age determination and applicable child/privacy/family rules |
| Regulated data/use | Required authorizations, claims substantiation and legal review |
| AI-generated content | Current applicable AI/content policies, reporting/safety, and provider data handling |

Do not force a nonexistent feature into the app. Unknown applicability cannot be marked not applicable. A fix that changes data behavior requires updated inventory, disclosures, policy and affected tests before rechecking.

Ready for submission is an engineering verdict scoped to observed evidence. Submitted, approved and released require separate store-state observations.
