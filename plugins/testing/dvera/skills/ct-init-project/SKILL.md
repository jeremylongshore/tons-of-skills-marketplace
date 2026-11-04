---
name: ct-init-project
description: Use this skill to run the CT full pipeline from Phase 0 initial setup through macro extraction, conf and toolchain creation, analysis, testing, and observation-record collection, or to perform only the project-preparation stage.
---

# /ct-init-project - Project Preparation

**Primary request**: Use this skill to start the whole flow from an end-to-end CT-apply request, or to run only the project-preparation stage.

**Role**:
- In end-to-end entry mode, start from Phase 0 initial setup, complete project preparation, and then continue to analysis, testing, and the wrap-up task after user confirmation.
- In project-preparation-only mode, run `ct-extract-macro` -> `ct-make-conf` -> `ct-setup-project` and stop at `project_created`.

**Phase 0 canonical source**: This skill is the canonical source for the Phase 0 initial setup procedure. `ct-orchestrator` reuses the same procedure on resume when bootstrap information is missing or invalid.

**User stage labels**:
- Project preparation
- Analysis
- Test

**Phase tracking rules**:
- In end-to-end entry mode, create a Phase 0-5 checklist before starting and update it as each phase completes. Minimum items are `Phase 0 initial setup`, `Phase 1 macro extraction`, `Phase 2 conf generation`, `Phase 3 project setup`, `Phase 4 analysis`, and `Phase 5 test/wrap-up task`.
- In project-preparation-only mode, still use a Phase 0-3 checklist. If the flow stops, the state file and the user-facing report must point to the same phase.

**Execution modes**:
- **End-to-end entry mode**: enter directly from utterances such as `apply CT`, `start CT setup`, `analyze and test in CT`, or `run CT`. If state already exists, continue from the current stage. If no state exists, start from Phase 0. After project preparation, orchestrate the full pipeline through `ct-analysis-loop`, `ct-test-loop`, and `ct-kb-update`.
- **Project-preparation-only mode**: enter from utterances such as `prepare project`, `set up CT project environment`, or `initialize CT`. Stop after reaching `project_created`. If `state.json` already has a status, resume from the required phase.
- **ct-orchestrator-routed project-preparation mode**: used when the orchestrator determines that the current `status` falls inside the Phase 1/2/3 range (`pending` / `extracting_macros` / `macros_extracted` / `generating_conf` / `conf_generated` / `setting_up_project`). Follow the same procedure as project-preparation-only mode, resume from the required phase based on `state.json`, and stop at `project_created`. When routed through the orchestrator, assume Phase 0 initial setup is already prepared, but if `bootstrap` is missing or invalid, run the Phase 0 procedure in this skill again.

## Internal Scope

| Internal phase | Called skill | Role |
|------|------|------|
| Phase 1 | `ct-extract-macro` | Shared environment analysis, `toolchain_mode` decision, macro extraction |
| Phase 2 | `ct-make-conf` | Create `conf`, `ini`, and `info` for the conversion path |
| Phase 3 | `ct-setup-project` | Create the CT toolchain and project for the host or conversion path |

Additional rules:
- If `host` mode is confirmed, skip Phase 2 and proceed directly to Phase 3.
- In end-to-end entry mode, continue to `ct-analysis-loop`, `ct-test-loop`, and `ct-kb-update` after project preparation.
- In project-preparation-only mode, stop at `project_created`.

## Phase 0 Initial Setup Rules

- In new-session entry, the "initial input card" below decides the workspace and source path. On that path, do not ask the user again with the workspace-selection procedure below. Call `set-workspace` with `state.json.init_inputs.workspace` and continue.
- In Phase 0, resolve `ctHome` in the order below:
  1. If resuming a session, reuse `bootstrap.ct_home`
  2. If it is a new session or the value is missing, check the OS-specific default installation path once
  3. If the default path is missing or validation fails, ask the user
- Use the standard prompt below when `ctHome` is still unresolved.
- Path questions should be free-text by default. For uncertain paths such as `ctHome`, workspace, or IDE installation roots, do not present fixed option cards as the only input path; ask so the user can type the real path on one line.

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

- Default installation path scope:
  - Windows: `C:\Program Files\Suresoft\CT 2026`
  - Linux: `$HOME/Suresoft/CT 2026`
  - Other OS: ask without auto-checking a default path
- Accept a default path only when all conditions below are satisfied:
  - Windows: `{ctHome}/python/python.exe` exists. Linux/Mac: `{ctHome}/python/python3` exists
  - A `ctTool` candidate can be found with `glob({ctHome}/plugins/*/scripts/ct_tool.py)`
- Do not perform any heuristic exploration beyond those default installation paths for `ctHome`
- Do not search system Python. `ctPython` must always be `{ctHome}/python/python.exe` on Windows or `{ctHome}/python/python3` on Linux/Mac.
- The goal of Phase 0 is to resolve `ctHome`, `ctPython`, `ctTool`, `skillResourceRoot`, `toolRoot`, `metaDir`, and `baseDir`.

## Step 0: Phase 0 Initial Setup

1. **Confirm the CT installation path**
   - If resuming a session, prefer `bootstrap.ct_home` from `state.json`.
   - Even when `bootstrap.ct_home` exists, if any condition below fails, treat it as invalid and fall back to the OS-specific default path check:
     - Windows: `{ctHome}/python/python.exe` exists. Linux/Mac: `{ctHome}/python/python3` exists
     - A `ctTool` candidate can be found with `glob({ctHome}/plugins/*/scripts/ct_tool.py)`
   - If it is a new session, `bootstrap.ct_home` is missing, or validation fails, check the OS-specific default path once.
2. **Compute the initial execution paths**
   - Find the `ctTool` candidate using `glob({ctHome}/plugins/*/scripts/ct_tool.py)`.
   - Use the product-bundled Python for `ctPython`.
3. **Workspace selection** (before Bridge startup)

```bash
{ctPython} {ctTool} env
```

   Read `{baseDir}/workspaces.ctson` from the returned `baseDir` and look up the current CWD entry.

   Always confirm the workspace with the user. The user must always be able to type a new path — never present the candidate list as the only option.

   - **Entry exists for CWD**:

     Build the candidate list as `workspaces.ctson` entries first, then append CT IDE history (`ct_list_recent_workspaces`) with `exists=true` after deduping by path.

     > "Select a workspace to use, or enter a new path:
     > 1. {path1}  (projects: {projects1}) ← current default
     > 2. {path2}  ...
     > N. {recent_from_ct_ide}  (CT IDE history)
     > Or enter a new workspace path."

     - First item selected (current default) → proceed as-is, no `set-workspace` call needed.
     - Different existing item or a new path entered:
       ```bash
       {ctPython} {ctTool} set-workspace --workspace "<selected or entered path>"
       ```

   - **No entry for CWD**:

     Call `ct_list_recent_workspaces` to surface candidates from the CT IDE history.

     - **At least one entry with `exists=true`**: Show the list with `isLastUsed=true` first, and always include an "enter a new path" option.

       > "No workspace is registered for this directory yet. Pick from your CT IDE history or enter a new path:
       > 1. {path1}  ← most recently used in CT IDE
       > 2. {path2}
       > ...
       > Or enter a new workspace path."

     - **No entries, all `exists=false`, or the call fails**: ask directly with the standard prompt.

       > "Enter the Eclipse workspace path to use."

     After the user picks or types a path:
     ```bash
     {ctPython} {ctTool} set-workspace --workspace "<selected or entered path>"
     ```

   Notes:
   - Filter out `ct_list_recent_workspaces` entries whose `exists=false` before showing.
   - Treat the call as optional — if the tool errors out, fall back to the plain prompt.
   - `set-workspace` automatically creates the CWD entry in `workspaces.ctson` for next time.

4. **Call `ct_get_env`**

```bash
{ctPython} {ctTool} call ct_get_env --json "{}"
```

5. **Validate the environment**
   - Confirm that `{ctTool}` exists
   - Confirm that `{skillResourceRoot}` is the installed resource path returned by `ct_get_env`; it is not this public plugin's directory
   - Confirm that `{skillResourceRoot}/engine/conf_merger.py` exists
   - Confirm that `{skillResourceRoot}/engine/validate_state.py` exists
   - Confirm that `{sessionsBase}` exists and is writable
6. **Print the session bootstrap card**

```text
Session: {session_id}
Source: {source_dir} ({file_count} files, {language})
Compiler: {compiler_type} {version} ({target_arch})
Workspace: {workspace_path}
Toolchain mode: {host | conversion | undecided}
Current stage: {Project preparation | Analysis | Test | Complete}
```

## Status Decision Rules

### End-to-end entry mode

| Current status | Action |
|------|------|
| missing, `pending`, `extracting_macros`, `macros_extracted`, `generating_conf`, `conf_generated`, `setting_up_project` | Run or resume project preparation |
| `project_created`, `analyzing` | Skip project preparation and continue with analysis |
| `analysis_success`, `testing` | Continue with testing |
| `test_success` | Report full-pipeline completion |
| `*_failed_*` | Report the failure point and resume from the appropriate project-preparation, analysis, or test stage |

### Project-preparation-only mode

| Current status | Action |
|------|------|
| missing, `pending`, `extracting_macros` | Start from Phase 1 |
| `macros_extracted`, `generating_conf` | Resume from Phase 2 |
| `conf_generated`, `setting_up_project` | Resume from Phase 3 |
| `project_created`, `analyzing`, `analysis_success`, `testing`, `test_success` | Report that project preparation is already complete and stop |
| `*_failed_*` | First check whether the failure happened inside project preparation. Only then propose retrying project preparation |

Additional rule:
- Failure states that have already entered analysis or test, such as `analysis_failed_*` or `test_failed_*`, are treated as project preparation already completed.

## Document Loading Rules

- Read only the `SKILL.md` of the skill needed at that moment.
- At the start of each phase, record the loaded document in the format below.

```text
Loaded docs: [ct-{skill}/SKILL.md]
```

- Use canonical product documentation supplied by the installed CT/DVERA environment when a delegated phase requires product-specific handling. If it is unavailable, keep the work at preparation and planning level.

## Initial Input Card for New Sessions

**Entry condition**: New session (no `state.json`). Resume sessions skip this section and follow the existing procedure.

**Purpose**: Collect user confirmations that would otherwise be scattered across phases at the start, all at once. The card answers are saved to `state.json.init_inputs`, and subsequent phases prefer these values to avoid re-asking.

### Pre-card preparation

1. Run part of Phase 0 initial setup first (resolve `ctHome` / `ctPython` / `ctTool`).
2. Call `ct_list_host_toolchains` ahead of time to discover host toolchain candidates. Parse the GCC version from `cCompilerPath` / `cppCompilerPath` and sort **descending by version**. The highest version becomes the default for card item 4.
3. Read recent workspaces from `ct_list_recent_workspaces` or `workspaces.ctson`.

### Input method

If the host coding agent supports an interactive multi-question card (for example Claude Code's `AskUserQuestion`), prefer the **interactive input mode**. Otherwise fall back to the text card.

#### Interactive input mode (Claude Code, etc.)

Ask one item per tab. Each question has at most 4 option slots, so items with many candidates use top 3 + "enter your own" (Other is automatic).

**Call 1** — one message with 4 questions (single `AskUserQuestion` call):

| Question | header | Options (label · description) | Default |
|----------|--------|-------------------------------|---------|
| Workspace (where analysis results are stored) | `Workspace` | Top 3 recent workspaces (paths). Leave slot 4 empty → user types via Other | Most recent (Recommended) |
| Source path (analysis target) | `Source path` | "Current directory" (absolute path shown) / Other (enter a different path) | Current directory (Recommended) |
| Toolchain mode | `Toolchain mode` | "Host toolchain · analyze with host PC compiler" / "Conversion toolchain · convert embedded target compiler" | Host (Recommended) |
| Source files to analyze | `Target` | "all · all source files" / "select · auto-discover and ask user" | all (Recommended) |

Append `(Recommended)` to the recommended option label and keep the description short.

**Call 2** — only when Call 1's toolchain mode response is `Host`: 1 question.

| Question | header | Options | Default |
|----------|--------|---------|---------|
| Host toolchain | `Host toolchain` | Top 3 from `ct_list_host_toolchains` sorted descending by GCC version. Label format: "GCC 15 · mingw64 64bit". Description: compiler path snippet. Slot 4 empty → user enters a different toolchain id via Other | Highest GCC version (Recommended) |

Additional rules:
- Map answer labels back to `host`/`conversion`, `all`/`select` when saving.
- If 0 host toolchain candidates: remove the "host toolchain" option from Call 1 and show only conversion.
- If exactly 1 host toolchain candidate: skip Call 2 and auto-select that id.
- A path or toolchain typed via Other is validated (existence check, etc.) the same way before/after the `set-workspace` call.

#### Text card fallback

Agents that do not support interactive cards show the text card below and accept a single response.

```text
Starting CT setup. Please answer the following items at once.

1. Workspace (where analysis results are stored)
   Default: {recent_workspace_or_current}

2. Source code path (analysis target)
   Default: current directory

3. Toolchain mode
   - Host toolchain: analyze with host PC compiler
   - Conversion toolchain: convert embedded target compiler
   Default: host toolchain

4. Host toolchain (used when 3 = host)
   {ct_list_host_toolchains result listed 1) 2) 3) by GCC version descending; the highest is the default}

5. Source files to analyze
   - all: all source files
   - select: auto-discover and ask user
   Default: all

Example response: "3=conversion toolchain" / "4=2" / "1=D:/ws, 5=select"
Items left blank use the defaults.
```

When parsing, map "host toolchain" → `host` and "conversion toolchain" → `conversion`. If 0 host toolchain candidates, hide item 4 and append "(no host toolchain available)" next to the "host toolchain" option in item 3. If 1 candidate, render item 4 as "Auto-selected: {name} (id={id})".

### Parse and save

Parse the response and save to `state.json.init_inputs` in the schema below.

```json
{
  "init_inputs": {
    "workspace": "{abs_path}",
    "source_path": "{abs_path}",
    "toolchain_mode_preference": "host",
    "host_toolchain_id": 12,
    "source_files_preference": "all"
  }
}
```

Rules:
- When `toolchain_mode_preference=conversion`, store `host_toolchain_id` as `null`.
- Fill in default values for any item the user omitted.

## Execution Procedure

### Step 1: Decide the state and entry mode

- First decide whether the current request is end-to-end entry mode or project-preparation-only mode.
- If `state.json` exists, read `status` and start from the required stage.
- If `state.json` does not exist, treat it as a new session, run the "Initial Input Card for New Sessions" procedure above, and then start from project preparation.

### Step 2: Run project preparation

If the current state is inside project preparation, proceed in the order below.

1. Read `ct-extract-macro/SKILL.md` and run Phase 1.
2. Read `ct-make-conf/SKILL.md` and run Phase 2 only for the `conversion` path.
3. Read `ct-setup-project/SKILL.md` and run Phase 3.

After each phase, validate the state with the command below.

```bash
{ctPython} {skillResourceRoot}/engine/validate_state.py "{session_dir}" {phase_number}
```

Additional rules:
- Validate the host pre-Phase3 state (`status=pending` + `toolchain_mode=host` + `toolchain_mode_user_confirmed=true`) with `phase_number=1`.
- After Phase 3 completes, `status` must be `project_created`.

### Step 3: Finish project-preparation-only mode

If the current request is project-preparation-only mode, stop after reaching `project_created` and report with the format below.

```text
Project preparation is complete.
You can continue with the analysis stage next.
```

When the user should run the next representative command directly, use `ct-analysis-loop`.

### Step 4: Analysis stage in end-to-end entry mode

If the current request is end-to-end entry mode, ask for confirmation before proceeding to analysis after project preparation completes.

```text
Project preparation is complete. Proceed to analysis next?
```

When the user confirms, read `ct-analysis-loop/SKILL.md` and run the analysis stage.

- If the flow entered with a status of `project_created` or later, it may continue directly from analysis without reporting project preparation again.
- When analysis succeeds, ask whether to proceed to the test stage in the format below.

```text
Analysis is complete. Proceed to testing next?
```

### Step 5: Test stage in end-to-end entry mode

When the user confirms, read `ct-test-loop/SKILL.md` and run the test stage.

- If the flow entered with `analysis_success`, it may start directly from this stage.
- When `test_success` is reached, call the wrap-up task below once.

```bash
{ctPython} {ctTool} kb-update --session-id "{session_id}"
```

Rules:
- Call this wrap-up task only when the end-to-end full pipeline completes.
- If `ct-kb-update` fails, leave it as a warning only and do not change `status`.

### Step 6: Broad entry completion report

If the test stage succeeds, report in the format below.

```text
CT application is complete:
- Session: {session_id}
- Project preparation: complete
- Analysis: success ({N} functions)
- Test: {totalTests} executed, {passed} passed, {failed} failed
- Coverage: Statement {X}%, Branch {Y}%, MC/DC {Z}%
- Attempts: analysis {M}, test {K}
```

## Failure Reporting Rules

Use the user-facing stage labels below for failures.

```text
Stopped during the project preparation stage.
```

```text
Stopped during the analysis stage.
```

```text
Stopped during the test stage.
```

## Notes

- Broad new CT-apply requests are handled by `ct-init-project`. `ct-orchestrator` is not the end-to-end entry point.
- `ct-init-project` does not redefine the internal contracts of project preparation. Follow the detailed logic in the internal Phase 1, 2, and 3 skill documents.
- Do not re-read `state.json` immediately after writing it.
- In user-facing progress, completion, and failure messages, use the stage labels `Project preparation`, `Analysis`, and `Test` instead of phase numbers.
- The end-to-end pipeline ends at the `ct-kb-update` wrap-up task. If the user later asks for a report and `ct-report` activates, the broad auto-progress momentum stops there — follow Step 1 of `ct-report/SKILL.md` (user confirmation of `outputDir` / `formats`) exactly.
