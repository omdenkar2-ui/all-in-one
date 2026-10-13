# AIO security modes and scope

Explicit user scope and execution authority govern. Keep the caller's journal, review/repair caps and original deadline. A mode narrows or selects evidence work; it does not authorize a repository-wide audit, extra agents, downloads, external probes or production effects.

| Operation | AIO contract |
| --- | --- |
| **static**, default | Inspect relevant source, callers, guards, configuration and dependency declarations as data. Trace attacker control, the violated boundary and concrete consequence. Do not run project setup, builds, tests, hooks, application code or scanners. Report supported static findings and unverified links. |
| `--comprehensive` | Add controlled reproduction only where the accepted task authorizes execution. Use disposable isolated state, synthetic identities/data, bounded attempts and legitimate/negative controls as described in [trust traces](trust-traces.md). Preserve the enforcing component and inspect real effects. Missing isolation, fixtures or execution authority leaves reproduction blocked while useful static assessment continues. |
| `--doctor` | Report prerequisites and readiness for a specified audit or reproduction: source access, versions, existing tools/fixtures, isolation and permissions. Inspect declarations and existing environment metadata only; no project/scanner/setup/test execution or downloads. Readiness is not an audit or finding verdict. |

`--doctor` and `--comprehensive` select alternative operations. Do not interpret doctor as permission to bootstrap the environment. Comprehensive does not require every available scanner or a repair candidate; authorized fixes still use the existing controller repair/review budget.

Select at most one audit scope below; reject conflicting selectors rather than silently combining them. With none, retain the accepted change and reachable trust paths. An explicitly requested full audit retains its named scope; static still defines its execution limit.

| Selector | Relevant backend paths |
| --- | --- |
| `--infra` | Deployment/IAM/secrets/network/configuration boundaries. |
| `--code` | Application input, authorization, tenant/data and effect boundaries. |
| `--skills` | Agent tools, MCP, skills/plugins/hooks and effective capabilities. |
| `--supply-chain` | Dependency/build/release inputs and executable reachability. |
| `--owasp` | Applicable web/API risk categories present in the backend; no conformance claim. |
| `--scope <domain>` | The named domain's paths and explicit coverage; clarify only a material unresolved domain boundary. |

`--diff` combines with an investigation scope and comprehensive: pin the accepted comparison base and current snapshot, including relevant uncommitted/untracked files. Read unchanged callers, guards, schemas and configuration needed to assess affected trust paths; keep unrelated variants as follow-up scope.

`--base <ref>` names the comparison base for diff work. Resolve it to the actual repository revision and retain that identity; a missing or ambiguous base blocks comparison rather than silently using another branch. Conflicting operations or scope selectors need a resolved choice before dependent audit work; earlier explicit user decisions remain effective.

`--offline` prohibits audit network calls, advisory lookups, scanner traffic and downloads. Use retained local evidence and disclose freshness gaps; it does not claim control of the host's model transport. `--budget <seconds>` can only narrow the original remaining deadline, including setup and cleanup; it never resets counters or extends time. Checkpoint unmet coverage at the limit.

Return operation, scope, assessed paths, evidence state and gaps separately from finding count. Runtime observations remain controlled AIO reproduction evidence; neither target logs nor these modes provide an authenticated gstack witness, exhaustive assurance or certification.
