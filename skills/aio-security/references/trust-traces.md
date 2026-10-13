# Change-relevant trust traces and security evidence

Read this when the accepted backend change touches, or newly reaches, agent tools, MCP configuration, skills/plugins/hooks, or dependency/build execution. Follow only relevant paths and nearby root-cause variants within the inherited scope and budget. An unrelated installed skill or optional global scan is not required coverage; global/user settings need an authorized source scope.

## Trace the effective capability

For each selected path, record: controlled input and actor -> parsing/interpretation -> validation and authorization -> executable or external effect -> tenant, credential, filesystem, network and resource capability. Verify callers, middleware and effective configuration rather than treating a filename, message role or manifest declaration as proof.

| Path | Questions that change the verdict |
| --- | --- |
| Agent/model/tool | Can a prompt, retrieval item, memory or tool result reach a consequential action? Do typed arguments and code outside the model enforce action/resource/tenant authorization, egress and spending limits? Can delegation or replay amplify privilege or paid work? |
| MCP server/client | Where is the caller identity bound to the session, audience, resource and consent? Can forwarded credentials or a server-controlled URL create a confused deputy or SSRF path? Which tools actually run with which local/remote capabilities? |
| Skill/plugin/hook/setup | Who controls installation/update content, command arguments, destinations and working directory? What executes on load, install or a hook event, with which inherited environment, credentials and external writes? Trace remote-content execution and interpolation; a familiar publisher, pinned revision or download command alone is not a verdict. |
| Dependency/build/release | Establish the installed/locked version, direct/transitive path and runtime or build reachability. Build dependencies may hold publish credentials. Trace attacker-controlled workflow input/artifact/cache to execution and effective write capability. An advisory, unpinned action or lifecycle script is a lead until exposure and impact are supported. |

Inspect configuration and source as data. Do not install/load an untrusted server, plugin or hook merely to inspect it, execute audit-supplied commands, test real credentials, or probe a deployed service without the task's existing authority. Use available trusted repository tools; missing tooling leaves a precise gap, not an invitation to install a scanner or widen scope. For a version-specific advisory, retain the actual affected-version source and freshness; unknown reachability stays unknown.

## Controlled exploit and repair evidence

Use disposable local state and synthetic identities/data. Preserve the component enforcing the boundary; mocking authorization, tenant lookup or the suspected vulnerable sink cannot prove its failure. A deterministic model fixture can demonstrate tool authorization behavior without establishing stochastic prompt exploitability.

Choose the smallest probe that exercises the claimed boundary. First establish legitimate behavior, then apply the attacker-controlled input or wrong owner/role/context. Inspect durable effects and disclosure as well as return values. A startup failure, generic nonzero exit or printed exploit claim is inconclusive. Retain setup/reset, exact input, expected invariant, observed effect, code/config/dependency snapshot and redacted evidence path. Stop only owned work and preserve evidence before cleanup.

Keep these judgments separate:

- **Candidate:** plausible path with a stated unverified link; never count it as a supported vulnerability.
- **Supported static finding:** traced attacker control, violated boundary and concrete consequence, with relevant guards/counterevidence inspected; runtime behavior remains untested.
- **Reproduced finding:** the intended security assertion fails under the controlled probe while its legitimate control works.
- **Verified repair:** the same security assertion and relevant legitimate/regression behavior pass on the declared repaired snapshot. Report test/provider and review limitations separately.

Assess severity from application impact and attacker prerequisites; confidence describes the evidence and unknowns. Scanner severity, agreement and missing hardening do not establish either. Use a skeptical pass within an existing review role to inspect alternative explanations and mitigations; it is not authority for extra reviewer dispatches.

Return assessed paths and gaps independently of the finding count. Say "No supported findings in the assessed scope" only after assessment, and keep blocked or inconclusive probes visible. Do not claim exhaustive standards conformance or authenticate target-produced logs beyond the actual harness's assurance.
