---
name: ct-self-healing
description: Run CT regression evidence collection after a C/C++ change and identify when the deployed CT Self-Healing workflow should review affected tests.
---

# CT Self-Healing Regression Review

Use this Skill after a C/C++ source, interface, build, or test-asset change when an existing CT test baseline must be re-run and affected tests may need Self-Healing review.

## CT installation check

If the CT installation path is missing or invalid, stop before reading the baseline or rerunning tests and show:

```text
The CT installation could not be verified.
Provide the installation path to continue.

[Installation check]
• Checked CT installation path: {ctHome or "not configured"}
• Requirement: CT 2026.06 or later with a valid license

[If CT is not installed]
• Product and installation support: bizcenter@suresofttech.com
```

## Purpose

This Skill performs the observable part of the workflow: it captures the available CT baseline, runs regression tests, collects new results and coverage, and classifies the affected tests for reuse, revision, or Self-Healing review.

The public `ct_tool.py` interface provides regression execution and evidence calls, but no standalone `ct_self_heal` command. Do not invent one or claim that a test was automatically repaired. When the deployed CT or Jenkins Self-Healing workflow is configured, use the resulting change record and failing-test evidence as its input.

## Entry conditions

Confirm the following before running tests:

- CT is installed and `{ctPython}`, `{ctTool}`, and `{projectName}` are resolved through `ct-test-loop/SKILL.md`.
- The CT project has completed a prior test run; a baseline result is available.
- The user identifies the relevant source, interface, build, or test-asset change.

If no prior result exists, stop and ask the user to establish it with `ct-test-loop` first.

## Capture the CT baseline

Before the next execution, request the stored result and coverage from CT.

```bash
{ctPython} {ctTool} call ct_get_test_results --json "@{results_payload_file}"
{ctPython} {ctTool} call ct_get_coverage --json "@{coverage_payload_file}"
```

```json
{ "projectName": "{projectName}" }
```

Record only the tests and coverage areas relevant to the stated change. Keep the baseline available for comparison after the run.

## Classify the change before execution

| Change pattern | CT follow-up | Review focus |
|---|---|---|
| Implementation changed; interface and expected behavior remain valid | Re-run existing tests | New failures and coverage delta |
| Renamed, moved, or structurally changed code; test intent remains valid | Self-Healing review candidate | Preserved intent and repaired test connection |
| Interface, behavior, requirement, or expected result changed | Test revision | Expected results, data, and requirement links |
| Compiler, macro, include path, toolchain, or target changed | Environment revalidation | Comparable build inputs before result comparison |

Do not classify an assertion or requirement change as a Self-Healing success case merely because the project builds.

## Run CT regression and collect evidence

Ask for confirmation before rerunning all registered CT tests.

```json
{
  "projectName": "{projectName}",
  "executeAll": true
}
```

```bash
{ctPython} {ctTool} call ct_execute_test --json "@{execute_payload_file}"
```

- If `testRunSuccess` is `false`, report the build or link failure. Do not collect a regression comparison or claim that Self-Healing ran. Continue with `ct-test-loop` or the installed Self-Healing workflow as appropriate.
- If `testRunSuccess` is `true`, request the new CT evidence.

```bash
{ctPython} {ctTool} call ct_get_test_results --json "@{new_results_payload_file}"
{ctPython} {ctTool} call ct_get_coverage --json "@{new_coverage_payload_file}"
```

Use `{ "projectName": "{projectName}" }` for both payloads.

## Compare and hand off

Compare test status by test name:

- **Regressed**: `Success` before, now `Failure` or `Error`
- **Recovered**: `Failure` or `Error` before, now `Success`
- **New failure**: newly added test now `Failure` or `Error`
- **Unchanged failure**: failure in both runs

Compare statement, branch, and MC/DC coverage with the baseline. Then report the change scope, CT execution result, test-status changes, coverage deltas, and next treatment: reuse, Self-Healing review, test revision, or environment clarification.

Use `ct-regression` when only the normal baseline comparison is needed. Use this Skill when that comparison must explicitly decide whether a source-structure change is a CT Self-Healing candidate.

CT 2026.06 or later and a valid CT license are required for product-backed verification. For a product demo, purchase, or deployment consultation, contact [bizcenter@suresofttech.com](mailto:bizcenter@suresofttech.com).
