---
name: aio-tdd
description: "Implement changed backend behavior through observed failing tests, minimal fixes and refactoring."
---

# AIO Tdd

Implement changed backend behavior through observed failing tests, minimal fixes and refactoring.

## Protocol

1. Choose the smallest observable behavior from the accepted unit and [verification playbook](../all-in-one/references/verification.md). State the invariant before selecting a test.
2. Write the boundary test first, run it and inspect the failure. Confirm the failure is the absent/wrong behavior, not broken setup. For a defect capture the actual reproducer; for an algorithm use an independent small-input oracle.

   When writing persistence fixtures, check setup/teardown independently before the behavioral suite and read the resource-lifecycle guidance in [aio-test](../aio-test/SKILL.md). A database transaction context is not necessarily a connection-closing context.
3. Implement the minimum correct behavior and rerun the test. Include duplicate delivery, races, crash/restart, invalid input and access boundaries that the changed contract exposes; avoid tests that merely repeat implementation details.

   For serialized tool/provider output, test the contract's actual JSON-serializable domain, including nested shapes and mixed key types when permitted. Keep canonical identity encoding separate from payload serialization: sorting mixed integer/string keys in a Python dict can reject a valid `json.dumps` input. Compare with an independent JSON roundtrip, then verify durable replay and copy isolation.
4. Refactor with relevant tests green, then exercise integration boundaries changed by the refactor. Record the observed red and green evidence and changed files for [aio-review](../aio-review/SKILL.md).
5. Reversible changes with no behavioral effect, such as formatting or documentation, may use appropriate nonbehavioral validation. Behavior-changing configuration still needs an observed failing boundary check. Isolated exploratory spikes are nonproduction experiments; hardening them requires the relevant behavioral proof. Record the concrete exception. Never delete user code merely to enforce a ritual.

## Return and handoff

A tested behavior change with red/green observations, refactor evidence and explicit exceptions. Unit completion still requires review and accepted checks.

In a pipeline, use the [stage contract](../all-in-one/references/stage-contracts.md) and return to the integrating controller. Run only this specialist's owned scope; preserve the user's accepted decisions and existing authorization.
