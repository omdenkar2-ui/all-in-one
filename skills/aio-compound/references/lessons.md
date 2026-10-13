# Durable backend lessons

## Eligibility and research

Apply this counterfactual: if the lesson disappeared, would a future engineer reading the final code, tests and contract likely repeat a material mistake or redo substantial investigation? If no, write nothing. An explicit compound request asks for that judgment, not an automatic file.

Eligible examples include a non-obvious provider idempotency limitation, a replay/versioning interaction, a migration lock failure unique to production distribution, or an algorithm assumption disproved by an adversarial input. Routine field renames, passing tests and obvious implementation summaries usually do not qualify.

Search with `rg` first in the project's existing lessons/docs and the core knowledge search for the invariant, symptom, provider/component and alternate vocabulary. Prefer an existing suitable record over a new duplicate. Read the actual code and evidence that establish the cause. Do not paste session history, entire logs, secrets, proprietary upstream text, or unverified tool output into a durable lesson.

## Original causal record

Use the normal project documentation location; absent one, `docs/aio/lessons/<descriptive-slug>.md` contained within the repository is sufficient. Record source revision, verified date and evidence references. Pin version-specific claims to the actually inspected runtime/provider version. A linked source may change; avoid describing a local snapshot as the latest release.

The lesson needs context and applicability, the violated invariant, an exact trigger, causal mechanism, discriminating evidence, remedy, operational/test consequence, rejected hypotheses that would otherwise mislead, and limitations. Explain why the final implementation alone would not reveal the reasoning. Keep one coherent cause per record; related causes can link rather than becoming a session dump.

Separate a verified fact from an inference. Describe a workaround as a workaround when the underlying external defect remains. Do not overgeneralize one provider or workload to all backends, impose a local business rule globally, or treat an incident mitigation as a permanent architecture law.

## Retrieval and maintenance

Preserve the project's current search/index format. A new plain Markdown index may list title, component, invariant, symptom terms and relative path; this makes `rg` retrieval available without changing the plugin's upstream source registry or installing a new database. Core bundled patterns and project-specific lessons remain separately attributed. If a project already has a database/index pipeline, update through its supported contract and validate it instead of hand-editing opaque storage.

Test two plausible queries using symptom and mechanism vocabulary. Verify the returned lesson distinguishes applicability, not just a generic keyword. All cited local paths should exist and stay inside the intended artifact scope; evidence with sensitive content should be summarized or linked under the project's access rules.

Before writing a new record, check whether the same root cause has an existing lesson. Update inaccurate context/remedy/test/version claims in place, retaining useful historical conditions and a short change note. Define refresh triggers: changed provider version, schema/checkpoint model, removed invariant, changed runtime or a contradictory new observation. A stale lesson should say what no longer applies, not silently instruct the next engineer to use an obsolete fix.

Do not add a discoverability rule to AGENTS.md or another instruction file without the task authorizing that change. Searchable local artifacts are enough. Return no-document with the eligibility reason when the code/tests or existing lesson already preserve the reasoning.
