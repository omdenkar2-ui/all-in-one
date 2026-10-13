---
name: aio-worktree
description: "Set up isolated backend work ownership without discarding or silently copying unrelated changes."
---

# AIO Worktree

Set up isolated backend work ownership without discarding or silently copying unrelated changes.

## Protocol

1. Inspect repository/status and available attached worktrees; prefer a suitable existing isolated checkout. Distinguish the actual repo from an ancestor directory containing unrelated user files.
2. Choose the user-specified ref or appropriate current task base, name owned paths/interfaces and preserve the original checkout. Never invent a starting branch that changes the accepted source.
3. Use the host managed-worktree capability when suitable, verify the returned path/attachment and run required setup/checks. Uncommitted work is not implicitly copied; handle needed changes explicitly.
4. Assign disjoint unit ownership and one canonical integrator. Archive/delete only task-owned disposable work after preserving needed artifacts and observed delivery; never blanket-reset a shared checkout.

## Return and handoff

A verified isolated checkout/ownership packet and setup evidence, with preserved user state.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
