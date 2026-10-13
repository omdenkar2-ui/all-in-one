# Configured local health mode

Use `--health` for a report-only dashboard of the caller's configured local backend checks. Default AIO Verify remains **implementation** or **completion** verification as resolved by the entrypoint. An explicit acceptance/completion request retains that gate; report any health dashboard separately and reuse only applicable evidence.

Resolve the exact check set from the accepted check configuration, repository contract or explicit user commands. Pin the current source/config/dependency snapshot and environment, including relevant uncommitted/untracked files. Do not invent a health stack, install tools, persist new repository configuration or add optional categories because a checker is available. With no configured set, return the prerequisite gap and unassessed coverage.

Use the existing [bounded check runner](check-runner.md) and `scripts/run_checks.py` for a configured dashboard; read its configuration, path, timeout and capture contract before use. Validate explicit argv/cwd/prerequisites, choose report-only checker options and leave an unavailable or mutating checker blocked rather than invoke autofix. Example, replacing paths with the accepted workspace/configuration:

```text
rtk proxy python "<aio-verify>/scripts/run_checks.py" checks.json --root "<workspace>" --validate
rtk proxy python "<aio-verify>/scripts/run_checks.py" checks.json --root "<workspace>"
```

Keep logs on disk and inspect complete outcomes, terminal exit codes, discovered/skipped counts and required environment gaps. Preserve runner statuses such as failed, timeout, missing_tool and incomplete_output; an exit-zero checker with missing assertions or zero discovered tests is not verified acceptance. Derive counts only from complete evidence, never a truncated prefix. Missing optional dimensions remain unassessed, not zero scores or passes.

Return a compact dashboard with check ID/purpose, actual command, result/exit code, duration, evidence path and material counts when observed. State the snapshot, configured coverage, baseline failures and limitations. Passing all configured checks means those checker observations passed; it does not prove all requirements, independent review, CI, delivery, security or deployed health. Do not calculate a composite health/readiness score or emit a full completion receipt from dashboard results.

This mode applies no fixes or publication. Recommendations return to the caller; separately authorized repairs belong to their implementation scope and existing repair/review caps. Retain the original controller journal, remaining deadline and limits for validation, execution and reporting; health mode does not start another run or launch extra agents. Unfinished checks remain pending or blocked with the exact next action.
