---
name: ct-report
description: Use this skill to export the test results and coverage of a CT project that has already been executed into a PDF/HTML/XLSX report.
---

# /ct-report - Generate Test Report

**Primary request**: Export the results and coverage of a CT project whose tests have already been executed as a document file.

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

**Precondition**: Phase 0 variables (`ctPython`, `ctTool`, `baseDir`) and `projectName` are acquired via the "Standalone entry procedure" in `ct-test-loop/SKILL.md` (Phase 0 Initial Setup from `ct-init-project` + CWD-keyed `projectName` lookup in `workspaces.ctson`).

## Execution Procedure

### Step 1: Confirm inputs (Stop-and-Ask)

**Definition of "confirmed"**: only values the user has **explicitly stated in this conversation** (in their utterance or as tool arguments) count as confirmed. Examples or defaults in this SKILL.md, `ct_generate_report`'s default, and values inferred by another skill do **not** count as confirmed.

If either `outputDir` or `formats` is unconfirmed, **do not proceed to Step 2 — ask first**.

- **Both unconfirmed**: bundle the two questions together, for example:

  > "I need two things to generate the report:
  > 1. Save location (e.g., `C:\reports\my-project`)
  > 2. Format: `pdf` / `html` / `xlsx` / `xls` / `docx` / `doc` / `pptx` / `ppt` (multiple allowed)"

- **Only `outputDir` unconfirmed**:
  > "Where should I save the report? (e.g., `C:\reports\my-project`)"
  - Normalize a relative path to an absolute path based on the current working directory.

- **Only `formats` unconfirmed**:
  > "Which format would you like? `pdf` / `html` / `xlsx` / `xls` / `docx` / `doc` / `pptx` / `ppt` (multiple allowed)"

This rule applies identically when this skill is chained from another skill. The auto-progress momentum of the upstream flow stops here.

### Step 2: Generate the report

```
ct_generate_report {
  "projectName": "{project_name}",
  "outputDir":   "{confirmed absolute path}",
  "formats":     ["{user-selected format}", ...]
}
```

- Pass `outputDir` as an **absolute path**.
- Wrap `formats` as a JSON array filled with the user's selection. Example: `["pdf", "html"]`

### Step 3: Report result

Read the `ct_generate_report` result before reporting anything. Report success only when the
call succeeded.

**On success**:

```
Report generated.
  Path:    {outputDir}
  Formats: {formats}
```

**On failure**: do not say the report was generated. Show what CT returned and stop.

```
Report generation failed.
  Project: {project_name}
  CT said: {error message}
```

The usual cause is a project whose tests have not been executed yet, since
`ct_generate_report` exports results that already exist. Direct the user to `ct-test-loop`
when that is the case.

## Guardrails

- **Do**: Normalize `outputDir` to an absolute path.
- **Don't**: Do not bundle multiple projects into one call (`ct_generate_report` is per-project).
- **Don't**: Do not rely on `ct_generate_report`'s default (`["pdf"]`) when `formats` is unconfirmed — Step 1 must ask the user first.
- **Stop and Ask**: If an unsupported format is requested, stop and list the supported formats: `pdf` / `html` / `xlsx` / `xls` / `docx` / `doc` / `pptx` / `ppt`.

## CT Functions

- `ct_generate_report(projectName, outputDir, formats?)` — generate report
  - `formats`: array, supports `pdf` / `html` / `xlsx` / `xls` / `docx` / `doc` / `pptx` / `ppt`
  - Returns: `{ outputDir, formats, message }`
  - The tool itself falls back to `["pdf"]` when `formats` is omitted, but **this skill must call it only after Step 1 has captured the user's choice**.
