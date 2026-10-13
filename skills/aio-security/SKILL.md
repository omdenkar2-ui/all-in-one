---
name: aio-security
description: "Audit backend trust boundaries, agent tools, tenant access and data exposure. Default to static inspection; use controlled reproduction and authorized hardening when requested."
---

# AIO Security

Audit backend trust boundaries, agent tools, tenant access and data exposure; harden only within accepted authorization.

Inherit the caller's [resource contract](../all-in-one/references/resource-budgets.md) and journal; use thorough for a standalone run. Bound investigation to the accepted change and its reachable trust paths. Existing review roles can cover this lens; it does not automatically add reviewers or a repository-wide audit.

Default to **static** source inspection with no project execution. Read [security modes](references/modes.md) for `--comprehensive`, `--doctor`, audit scope selectors, `--diff`, `--offline` or `--budget`; resolve them before investigation. `--doctor` returns readiness only; investigations follow the protocol below. An explicitly authorized reproduction request uses the bounded comprehensive path for that boundary. AIO evidence does not acquire gstack's trusted runtime witness or certification.

## Protocol

1. Build a bounded threat model around real assets, actors, privileged operations and entry points. Read [security](../all-in-one/references/security.md) and identify what the change exposes.
2. Trace trusted auth context to resource authorization across APIs, queues, webhooks, checkpoints and tools. Model text, object/run IDs and signed events cannot substitute for resource/business-state checks.
3. Inspect secret/log/prompt handling, retention, provider scopes, input/resource bounds and relevant abuse paths. For arbitrary URL tools consider redirects, DNS/network boundaries and SSRF. When agent/MCP configuration, skills, plugins, hooks or dependency/build paths affect the change, read [trust traces and evidence](references/trust-traces.md); follow the controlled input to the effective capability.
4. Challenge protective middleware, callers and configuration before promoting a candidate. Static mode stops at source-supported findings without running the project. Under authorized comprehensive reproduction, use synthetic, isolated evidence and legitimate/negative controls. Static reasoning, scanner leads and runtime observations remain distinct.
5. Return severity, confidence, consequence, source location, evidence state and concrete repair/verification. Apply only authorized fixes through the controller's repair scope; runtime verification requires the permitted reproduction path. Retain unavailable checks honestly; a scoped result is not a security certificate.

## Return and handoff

A scoped threat model and actionable security findings or verified repairs with assessed paths, unresolved hypotheses and remaining coverage.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
