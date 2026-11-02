---
name: ct-regression
description: Use after a code change to rerun existing tests and report regression status (new failures and coverage deltas).
---

# /ct-regression — Regression Testing After Code Changes

**Primary request**: After a code change, confirm that existing tests still pass and report new test failures and coverage deltas.

## CT Installation Check Failure

If the CT installation path is missing or validation fails, do not continue. Show the notice below.

```text
The CT installation could not be verified.
Provide the installation path to continue.

[Installation check]
• Checked CT installation path: {ctHome or "not configured"}
• Requirement: CT 2026.06 or later
• Note: A valid CT license is required to run CT.

[If CT is already installed]
• Please provide the full path to the CT installation folder.
  Example: C:\Program Files\Suresoft\CT 2026

[If CT is not installed]
• Product and installation support: bizcenter@suresofttech.com
```

**Entry**: A CT project with a prior test-result baseline
**Input (standalone)**: `workspaces.ctson` entry keyed by CWD -> `projectName`. Baseline is fetched via `ct_get_test_results(projectName)` and `ct_get_coverage(projectName)`.
**Input (orchestrator-routed)**: in-memory state -> `ct_resources.project_name`, prior `test_results`, prior `coverage`
**Output (orchestrator-routed)**: in-memory state update (`status=regression_done`, adds a `regression` field)

**Standalone guard**: At standalone entry, verify in two steps.
1. **Project registration**: If `workspaces.ctson` has no entry keyed by CWD -> **stop immediately** and tell the user "This directory is not registered as a CT project. Run `ct-init-project` first."
2. **Baseline existence**: Call `ct_get_test_results(projectName)`. If empty -> **stop immediately** and tell the user "No baseline test results. Run `ct-test-loop` first to generate and run tests."

**Prerequisite**: For standalone entry, follow `ct-test-loop/SKILL.md`'s "Standalone entry procedure" to acquire the Phase 0 environment and `projectName`.

## Shared File/Encoding Rules

Apply the shared file/encoding rules from ct-test-loop SKILL.md as-is.

## Steps

### Step 1: Load baseline

Save the prior results as the baseline.

- **Orchestrator-routed**: use `test_results` and `coverage` from the in-memory state as-is.
- **Standalone**: use the values returned by `ct_get_test_results(projectName)` and `ct_get_coverage(projectName)`.

```
baseline = {
  "test_results": <prior test_results>,
  "coverage":     <prior coverage>
}
```

### Step 2: Rerun tests

Rerun tests after the code change.

```
ct_execute_test {
  "projectName": "{project_name}",
  "executeAll":  true
}
```

**`testRunSuccess == false`** (build failure) → report to the user and stop.
- Report: "Build failed. There are compile/link errors introduced by the code change. Use ct-test-loop to fix them."
- Regression testing is only meaningful on a successful build.

**`testRunSuccess == true`** (build success) → proceed to Step 3.

### Step 3: Collect results

```
ct_get_test_results { "projectName": "{project_name}" }
ct_get_coverage     { "projectName": "{project_name}" }
```

### Step 4: Regression analysis

Compare the baseline against the new results.

**Test comparison** (keyed by test name; statuses come from `ct_get_test_results` and use `Success`/`Failure`/`Error`/`NotOperated`/`Ignore`):
- `regressed`: previously `Success`, now `Failure`/`Error`
- `recovered`: previously `Failure`/`Error`, now `Success`
- `new_failures`: tests newly added this run that are `Failure`/`Error`
- `unchanged_failures`: `Failure` in both runs

**Coverage comparison**:
- Compute the delta for Statement, Branch, and MC-DC against the baseline.

### Step 5: Report

Report in the following format.

```
Regression Test Result

  Total: {total} / Passed: {passed} / Failed: {failed}

  ⚠️  New failures ({regressed}):
    - {testName} ({suiteName})  ← previously Success → now Failure/Error

  ✅  Recovered ({recovered}):
    - {testName} ({suiteName})  ← previously Failure/Error → now Success

  Coverage delta:
    Statement: {prev} → {curr}  ({delta})
    Branch:    {prev} → {curr}  ({delta})
    MC-DC:     {prev} → {curr}  ({delta})
```

- If `regressed == 0`, report "No regression — all previous tests still pass."
- If `regressed > 0`, list the failures and ask the user for next steps.

### Step 6: Apply results (per mode)

Handle this differently per entry mode. Standalone does not reference `state.json`, so there is nothing to update.

- **Standalone**: end at the Step 5 report with no state update. The baseline and results are re-fetched each run via `ct_get_test_results` / `ct_get_coverage`, so no persistent state is created.
- **Orchestrator-routed**: update the in-memory state as below (`status=regression_done`, add a `regression` field). Whether and when to write to disk `state.json` follows ct-orchestrator's state rules.

```json
{
  "status": "regression_done",
  "regression": {
    "baseline_status": "test_success",
    "regressed": [...],
    "recovered": [...],
    "new_failures": [...],
    "coverage_delta": {
      "statement": "+2%",
      "branch": "-1%",
      "mcdc": "0%"
    }
  },
  "test_results": { ... },
  "coverage": { ... }
}
```

## Guardrails

- **Do**:
  - Always distinguish a build failure from a test failure.
  - If the baseline is missing, stop immediately and point the user to ct-test-loop.
  - Compare by test name.
- **Don't**:
  - When `testRunSuccess == false`, do not collect test results or attempt comparison.
  - Do not treat assertion failures as environment issues.
  - Do not attempt to fix build errors inside this skill.
- **Stop and Ask**:
  - If `regressed > 0`, do not attempt fixes automatically — report to the user and ask what to do next.

## CT Functions (used by this skill)

- `ct_execute_test(projectName, executeAll)` — rerun all tests
- `ct_get_test_results(projectName)` — fetch the new test results
- `ct_get_coverage(projectName)` — fetch the new coverage
- `ct_generate_report(projectName, outputDir, formats?)` — generate a report (optional). `formats` accepts one or more of `pdf`, `html`, `xlsx`, `xls`, `docx`, `doc`, `pptx`, `ppt` (defaults to `["pdf"]`)
