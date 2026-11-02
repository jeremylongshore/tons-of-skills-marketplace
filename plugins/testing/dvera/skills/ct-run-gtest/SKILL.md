---
name: ct-run-gtest
description: Re-run GoogleTest assets already registered in a CT project, then review their execution results and structural coverage.
---

# CT GoogleTest Reuse and Verification

Use this Skill when a CT project already contains GoogleTest assets and a team needs to re-run them after a source, build, or test-code change.

## CT installation check

If the CT installation path is missing or invalid, stop before collecting or executing test evidence and show:

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

This is an **existing-test reuse** flow. It preserves developer-owned GoogleTest code, executes the CT project, and collects the resulting test and coverage evidence.

CT can import and manage GoogleTest projects and test code. The public `ct_tool.py` interface does not expose a separate GoogleTest import command, so register or import the assets through the deployed CT workflow before using this Skill. Do not claim that this Skill imported or converted GoogleTest code.

## Entry conditions

Before running CT, confirm all of the following:

- CT is installed and its product-bundled Python and `ct_tool.py` path are resolved.
- The current directory is registered in `workspaces.ctson` and has a CT `projectName`.
- The project was analyzed successfully; `ct_get_functions` returns one or more functions.
- The relevant GoogleTest suites, fixtures, and test data are already registered in the CT project.

For a standalone request, use the Phase 0 environment procedure in `ct-test-loop/SKILL.md` to resolve `{ctPython}`, `{ctTool}`, and `{projectName}`. If the project is not ready, direct the user to `ct-init-project` and then `ct-analysis-loop`.

## Verify the project and test scope

First confirm that the CT project remains analyzable.

```bash
{ctPython} {ctTool} call ct_get_functions --json "@{payload_file}"
```

```json
{ "projectName": "{projectName}" }
```

If no functions are returned, stop and ask the user to complete `ct-analysis-loop` first.

Then record the test assets to be exercised.

| Asset | Target behavior or source area | Change impact | Expected evidence |
|---|---|---|---|
| GoogleTest suite, case, fixture, stub, mock, or test data | Function, module, or interface | Reuse, review, or environment clarification | Result and statement/branch/MC/DC coverage |

Do not infer that a passing build proves that each existing test still has valid intent or expected results.

## Execute the registered tests in CT

Ask for confirmation before executing all tests. Create the JSON payload with a serializer-backed temporary file, then call the installed CT tool.

```json
{
  "projectName": "{projectName}",
  "executeAll": true
}
```

```bash
{ctPython} {ctTool} call ct_execute_test --json "@{payload_file}"
```

- If `testRunSuccess` is `false`, report a build or link failure and stop. Do not classify it as a GoogleTest assertion failure.
- If `testRunSuccess` is `true`, collect results and coverage before drawing conclusions.

## Collect CT evidence

```bash
{ctPython} {ctTool} call ct_get_test_results --json "@{results_payload_file}"
{ctPython} {ctTool} call ct_get_coverage --json "@{coverage_payload_file}"
```

```json
{ "projectName": "{projectName}" }
```

Review the returned status for each test (`Success`, `Failure`, `Error`, `NotOperated`, or `Ignore`) with the relevant statement, branch, and MC/DC coverage values.

If a reviewable report is needed, first ask the user for its output directory and formats, then use `ct-report` rather than assuming a location or format.

## Result handoff

Report the GoogleTest assets in scope, CT execution result, failing or error-status tests, returned coverage, and any remaining intent, requirement, or environment question.

For change comparison against an earlier result, continue with `ct-regression`. For generation or repair of tests, continue with `ct-test-loop`; do not overwrite developer-owned GoogleTest assets automatically.

CT 2026.06 or later and a valid CT license are required for product-backed verification. For a product demo, purchase, or deployment consultation, contact [bizcenter@suresofttech.com](mailto:bizcenter@suresofttech.com).
