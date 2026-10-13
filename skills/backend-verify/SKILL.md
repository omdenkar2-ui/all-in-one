---
name: backend-verify
description: "Run backend acceptance, integration, recovery and resource checks and validate completion evidence."
---

# backend-verify: compatibility entrypoint

Use [aio-verify](../aio-verify/SKILL.md) for this backend stage. Preserve the exact accepted request, source, scope and evidence when delegating. This older invocation remains supported; the canonical AIO skill supplies the current procedure.

When another controller invokes this alias, return its stage artifacts, findings and next action to that caller. Do not start a second whole-project pipeline or claim final delivery from a focused stage.
