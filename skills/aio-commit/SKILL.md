---
name: aio-commit
description: "Create a focused local commit after inspecting owned backend changes and validation evidence."
---

# AIO Commit

Create a focused local commit after inspecting owned backend changes and validation evidence.

## Protocol

1. Confirm the intended repository/worktree, branch and owned files. Inspect status/diff and preserve unrelated user changes; never stage an ancestor home repository by accident.
2. Review the selected diff for secrets, generated/scratch files, conflicts and consistency with acceptance. Include required source/tests/docs/migrations as one coherent change.
3. Check relevant test evidence is for the current source and inspect whitespace/conflict checks. Preserve intentionally unchanged vendored files and disclose upstream formatting warnings separately.
4. Inspect the index before staging. Preserve unrelated staged user changes and use a path-limited commit, such as `git commit --only -- <owned-paths>`, when needed to keep them out of this commit. Commit with a problem/result-oriented message and inspect its exact file set plus remaining status; a local commit does not imply push, PR or deployment.

## Return and handoff

An observed local commit ID, owned scope, validation and remaining working-tree state.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
