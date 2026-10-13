---
name: aio-proof
description: "Collect reproducible backend acceptance evidence bound to source and candidate artifacts."
---

# AIO Proof

Collect reproducible backend acceptance evidence bound to source and candidate artifacts.

## Protocol

1. Choose the claim and R/V IDs, exact source/revision/build and observation boundary. Determine which evidence needs local tests, a real provider, live service or console access.
2. Execute the relevant checks and save raw commands, environment, timestamps, exit status and assertions without secrets. Distinguish mocks/synthetic fixtures from operational proof.
3. Bind artifacts to hashes and verify links/files resolve under the workspace. Inspect remote PR/deploy/service state separately; do not turn arbitrary local files into proof of remote success.
4. Package a minimal evidence dossier and run the appropriate completion/launch gates. Any unavailable required observation stays unverified and goes to [aio-verify](../aio-verify/SKILL.md).

## Return and handoff

A source-bound reproducible proof dossier with actual observations and precisely limited claims.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
