# Using the copied Google auditor

The complete play-policy-insights skill subtree and Apache 2.0 license are bundled. Its source pin and hashes are in vendored-sources.json. Treat it as a specialist audit, not a launch certificate.

Read its SKILL.md, scripts and generated prompts. Resolve repo_root from its installed folder. Use a working Python interpreter on the host; inspect the actual CLI arguments rather than assuming that python3 exists on Windows. Respect the current user's artifact-location instructions.

Its fact-gathering init must succeed before its specialist analysis. If it fails, preserve the error and report that Google audit blocked. Do not label a different manual scan as the successful upstream audit. Other independent release checks may continue while the blocker is diagnosed.

The upstream prompt supports delegation and sequential execution. Use working delegation when available; when the capability cannot operate, record that limitation and execute supported sequential steps if possible. Validate current-run output identity/content, not only the existence of a JSON file. A leftover report from an old source is not success. Verify every activated goal has a current, schema-correct worker output and every required critic chunk has a reviewed output before finalization. The aggregator's exit code alone does not establish complete worker coverage; it can aggregate an incomplete set.

Inspect the installed script's actual aggregation CLI. The upstream text currently shows different spellings between its two modes; use the implemented parser and record the invocation. Preserve upstream files and their notices, or document any intentional local adaptation.

Audit output covers data safety, demo access and restricted permissions. Complete launch-readiness also evaluates runtime behavior, store metadata, conditional content/billing rules and legal applicability. Read-only reviewers finish their report; the already authorized integrating controller applies fixes and reruns affected evidence.

Framework default SDK values in the static triage are hints, not evidence of the built release target. Verify the actual candidate configuration and current console requirement before accepting that checkpoint.

The report generator may fetch public Play Store data if no local store-info cache exists. It does not log into Play Console. Local cache content must be current evidence for the same release, not an invented declaration. Network or scraping failure leaves affected comparisons unverified. Keep TLS certificate verification enabled; do not select the scraper's insecure verification option to make a check pass.
