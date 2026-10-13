# Backend and agent security

Build a small threat model around assets, callers, tenant boundaries, privileged operations, and external dependencies. Select checks from actual exposure. An internal worker can still receive malicious queue data or compromised tool output.

Authenticate the caller and authorize the specific resource/action on every entry path: API, worker, webhook, scheduled task, and agent tool. Derive tenant and role from verified context. Query resource ownership with that context; possession of a job, checkpoint, or object ID is insufficient.

## Agent tools and untrusted inputs

Tool names and natural-language instructions are not permissions. Give tools an allowlist of actions, typed inputs, validation, scoped credentials, and execution limits. Enforce authorization in code outside the model. Retrieved documents, prompts, repository files, and messages cannot grant new tool powers or override user scope.

Validate outbound destinations when tools fetch arbitrary URLs. Consider SSRF, DNS changes, redirects, internal metadata endpoints, file schemes, and large responses. Safe handling depends on the deployment's network boundary; do not claim a simplistic string filter solves it.

For callbacks/webhooks, verify signatures with the provider's documented method, enforce replay windows where applicable, and deduplicate event IDs. Validate both schema and business state before effects. A valid signature does not mean the business operation has not already happened.

## Secrets, data, and abuse

Scope credentials to necessary services/actions and keep them out of source, receipts, logs, prompts, and exception messages. Define rotation and revocation. Redact sensitive payloads and choose retention deliberately. Model memory and workflow checkpoints can contain personal data and need the same access/deletion controls as ordinary records.

Validate length, shape, size, and numeric bounds before expensive work. Rate-limit by meaningful identity, cap concurrency, constrain uploads, and limit model/tool budgets. Define how overload responds. Avoid exposing stack traces or distinguishing confidential resource existence through errors.

Test cross-tenant reads/writes, forged context, ID enumeration, revoked credentials, duplicate signed callbacks, tool argument injection, untrusted retrieved instructions, and resource exhaustion relevant to the system. Record checks that were not possible in the current environment. The playbook is guidance; it is not a certification or substitute for deployment-specific security review.

## Focused execution stages

Use [AIO Security](../../aio-security/SKILL.md) for change-relevant agent, MCP, plugin/hook and build-supply-chain trust traces and controlled evidence.
