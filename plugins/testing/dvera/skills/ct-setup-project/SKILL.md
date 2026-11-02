---
name: ct-setup-project
description: Use this skill to create the CT toolchain and project for the host or conversion path, and to apply user include paths and defines as compile flags.
---

# /ct-setup-project - Project Creation (Phase 3)

**Primary request**: Use this skill when creating a CT project and toolchain with either a host or conversion toolchain.

**Entry**:
- `conversion`: `status` is `conf_generated`
- `host`: `status` is `pending` or missing, `toolchain_mode=host`, and `toolchain_mode_user_confirmed=true`
**Input**: `state.json` -> shared `toolchain_mode`, `source_info`, `project_inputs`; for `conversion`, also top-level `conf_path`, `artifacts.meta_ini_path`, `artifacts.meta_info_path`, `env_profile.resolved_vars`, and `env_profile.system_headers` (must already be populated as a non-empty list in Phase 1)
**Output**: `state.json` (`status=project_created`, `ct_resources.*`, and either `host_toolchain` or `fingerprints`)
**Execution mode**: In-memory state when called through `ct-orchestrator` / one-time `state.json` read in standalone mode
**Standalone guard**:
- If `toolchain_mode` is missing or unresolved -> **stop immediately** and tell the user to run `ct-init-project` first to complete project preparation
- If it is `conversion` but `status` is not `conf_generated` -> **stop immediately** and tell the user to run `ct-init-project` first to complete project preparation
- If it is `conversion` but `env_profile.system_headers` is missing or empty -> **stop immediately** and tell the user to run `ct-init-project` first to complete project preparation. `system_headers` must not be empty
- If it is `host` but pre-Phase3 fields (`toolchain_mode_evidence`, `toolchain_mode_user_confirmed`, `source_info`, `project_inputs`) are missing -> **stop immediately** and tell the user to run `ct-init-project` first to complete project preparation
- In `conversion`, toolchain creation is impossible without the Phase 2 artifacts (top-level `conf_path`, `artifacts.meta_ini_path`, `artifacts.meta_info_path`)
**Precondition**: Use the bootstrap variables acquired in Phase 0. In end-to-end entry, `ct-init-project` prepares them. In resume entry, `ct-orchestrator` prepares them. Even in standalone mode, run the bootstrap procedure below first.

## Shared File and Encoding Rules

- Read and write all text files using **UTF-8 without BOM** by default.
- Python scripts must accept both BOM and no-BOM on read, and always write files as UTF-8 without BOM.
- Apply this rule to phase output text files such as `state.json`, `compiler_info.json`, `observations.jsonl`, `.conf`, `.ini`, and `.info`.
- Do not build JSON or JSONL by concatenating strings. Always use serializers such as `json.dump` or `json.dumps`.
- When exchanging JSON or text through process `stdout`, `stderr`, pipes, or redirects, handle everything as UTF-8.
- Minimize inline execution such as `python -c`. When paths, JSON, and Python code are nested in one string, encoding and escaping failures become much more likely.
- Store paths written into `state.json`, JSON payloads, and logs or metadata as **absolute paths**, and normalize to `/` when it is safe to do so.
- Do not force blanket `/` normalization for paths passed to external process `argv`. Use `argv` lists by default, and only use `/` normalization when the target tool is known to accept it safely.
- Use `LF` as the default line ending for newly created internal management files such as `state.json`, `compiler_info.json`, and `observations.jsonl`. Preserve existing line endings when editing an existing file.
- Do not rewrite existing artifacts only for encoding normalization. Unnecessary rewrites can change fingerprints.
- Build JSON payloads with a serializer-backed temporary file by default. Prefer Python `json.dump(..., ensure_ascii=False)` with `tempfile.NamedTemporaryFile(delete=False, encoding="utf-8")` or `tempfile.gettempdir()`, then pass it as `ct_tool.py call ... --json "@{path}"`.
  - Do not hand-escape path strings. Let the JSON serializer handle Windows backslashes and non-ASCII text.
  - Use `@-` stdin only as a secondary input channel.
  - PowerShell `ConvertTo-Json` is a Windows-only auxiliary option; Bash heredoc/cat examples must not be the default payload path.
- Even for simple payloads, prefer a temporary JSON file or `argv` lists over one-line string payloads.
- Build Phase 3 payloads through one serializer-backed flow. After `ct_create_toolchain`, patch only the returned `toolchainId` into the project payload temporary JSON; do not split this into two persistent helper scripts such as `phase3_payload.py` and `add_tc_id.py`.

## Execution Guardrails

- **Do**:
  - Branch on `toolchain_mode` first and never mix the host and conversion write scopes.
  - Resolve real `sourceFiles` from `source_info.source_paths` before calling `ct_create_project`.
  - In `conversion`, validate top-level `conf_path`, `artifacts.meta_ini_path`, and `artifacts.meta_info_path` as absolute paths before creating the toolchain.
  - Build `ct_set_compile_flags` input only from `project_inputs.include_paths.user` and `project_inputs.defines`.
- **Do not**:
  - Create conversion-only outputs (`conf`, `ini`, `info`, `fingerprints`) in `host` mode.
  - Call `ct_create_project` with only `sourceDir` and omit `sourceFiles` in `conversion` mode.
  - Mix user includes into `systemHeaders` or put system headers back into `compileFlags`.
  - Treat `compiler_info.include_paths.system` as the canonical source for `ct_set_compile_flags`.
- **Why**:
  - Mixed inputs in Phase 3 make Phase 4/5 fail at the more basic question of which mode to trust, before you can even reason about why it failed.
- **Stop and Ask summary**:
  - If there are 2 or more source files and `selected_source_files` is not fixed yet, stop and confirm.
  - If there are multiple host toolchain candidates and the selection basis is not resolved, stop and confirm.
  - In `conversion`, if IDE variable path resolution is incomplete or the source directory itself is invalid, stop and confirm.
- **Safe pattern**:

```text
if toolchain_mode == "host":
  write only the host toolchain selection result
  ct_create_project(..., sourceFiles=[...], toolchainId=host_id)
else:
  validate absolute conf/ini/info paths
  ct_create_toolchain(...)
  ct_create_project(..., sourceFiles=[...], toolchainId=created_id)
```

## Pre-Work Gate Check

1. Confirm that `toolchain_mode` and `toolchain_mode_user_confirmed` are fixed.
2. Confirm that the actual list to use as `sourceFiles` is fixed in either `selected_source_files` or `source_info.source_paths`.
3. Confirm which branch, `host` or `conversion`, will run and which state write set is allowed in that branch.
4. If it is `conversion`, confirm that top-level `conf_path` and the `artifacts.conf_path` mirror point to the same absolute path.
5. Confirm that compile flag input is built only from `project_inputs.*`.

**Standalone bootstrap procedure**:
1. If `bootstrap.ct_home` exists in `state.json`, use that value.
   - However, if either of the conditions below fails, treat the value as **invalid** and fall back to one-time OS-specific default installation path checking.
     - Windows: `{ctHome}/python/python.exe` exists. Linux/Mac: `{ctHome}/python/python3` exists
     - A `ctTool` candidate can be found with `glob({ctHome}/plugins/*/scripts/ct_tool.py)`
   - If `bootstrap.ct_home` is missing or validation fails, check the OS-specific default installation path once.
   - Windows: `C:\Program Files\Suresoft\CT 2026`
   - Linux: `$HOME/Suresoft/CT 2026`
   - For other OS types, do not auto-check a default path. Ask the user for `ctHome` with the **standard prompt** below.
   - Use the default installation path only when both conditions below are satisfied.
     - Windows: `{ctHome}/python/python.exe` exists. Linux/Mac: `{ctHome}/python/python3` exists
     - A `ctTool` candidate can be found with `glob({ctHome}/plugins/*/scripts/ct_tool.py)`
   - If the default path does not exist or validation fails, ask the user for `ctHome` with the **standard prompt** below.
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
2. `ctPython` candidate: Windows -> `{ctHome}/python/python.exe`, Linux/Mac -> `{ctHome}/python/python3`
3. `ctTool` candidate: `glob({ctHome}/plugins/*/scripts/ct_tool.py)`
4. **Workspace selection** (before Bridge startup)
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
5. Call `ct_get_env` to acquire `pythonPath`, `skillResourceRoot`, `toolRoot`, `metaDir`, and `baseDir`.
   ```bash
   {ctPython} {ctTool} call ct_get_env --json "{}"
   ```
6. Normalize `ctPython`, `ctTool`, and `skillResourceRoot` from the returned values.
7. Once `sessionsBase` is known, search for the latest session's `state.json` under `{sessionsBase}/`.
   - If there are multiple sessions, show the list and ask the user to choose.

**Bootstrap variables** (acquired in Phase 0; end-to-end entry via `ct-init-project`, resume entry via `ct-orchestrator`, or by the standalone procedure above):
- `{ctPython}`: Python executable path based on `ct_get_env.pythonPath`
- `{ctTool}`: `ct_tool.py` execution path
- `skillResourceRoot`: autoconfig path from `ct_get_env.skillResourceRoot`
- `metaDir`: metadata path from `ct_get_env.metaDir`
- `sessionsBase`: workspace base path from `{baseDir}/sessions/ (derived)`

**CT functions** (used in Phase 3):
- `ct_list_host_toolchains()` - list registered host toolchains
- `ct_list_toolchains(nameFilter?)` - list all toolchains when name or description inspection is needed
- `ct_create_toolchain(toolchainName, confFilePath, infoFilePath, iniFilePath?, systemHeaders?)` - **`infoFilePath` is required**
- `ct_create_project(sourceDir, sourceFiles, projectName, toolchainId?)` - specify the toolchain with `toolchainId`
- `ct_set_project_toolchain(projectName, toolchainId)` - change the project toolchain for initial Phase 3 setup. **Do not call this after `ct_modify_toolchain`**
- `ct_get_project_settings(projectName)` -> extract `workingDirectory`
- `ct_set_compile_flags(projectName, compileFlags)` - only for user includes and defines

**User confirmation (required before entering Phase 3 - ask one by one in order)**:

**init_inputs preset rule**: if `state.json.init_inputs` exists, the two confirmations below are auto-decided from those values and not asked again.
- If `init_inputs.source_files_preference="all"`, Confirmation 1 is auto-resolved as "select all". If `"select"`, ask the user using the existing procedure.
- If `init_inputs.host_toolchain_id` exists, Confirmation 2 auto-selects the candidate with that id.

### Confirmation 1: Source File Scope

- **If there is only one source file**: proceed with that file without asking.
- **If there are 2 or more source files**: show the list from `source_info.source_paths` and ask the question below. **Ask confirmation 2 only after this answer is received.**

  > "Should I create the project with all of these source files ({N}), or would you like to select specific files only?"

  - **Select all**: use `source_info.source_paths` as-is
  - **Select specific files**: show the list again and store only the selected files in `selected_source_files`, then use that list for `ct_create_project.sourceFiles`

### Confirmation 2: Host Toolchain Selection (host mode only)

Proceed only after confirmation 1 is answered.

- Skip this confirmation in `conversion` mode.
- In `host` mode, use the result of `ct_list_host_toolchains()`.
  - If there is only one candidate, select it automatically and report that result.
  - If there are 2 or more candidates, show the list with the selection basis and ask the user to confirm.
  - Record the final selection in `host_toolchain` inside state.

---

**Core sequence**:
1. Load input and **normalize all paths to absolute paths**
   - Shared: `toolchain_mode`, `source_info`, `project_inputs`
   - `conversion`: **resolve IDE variables** by replacing `${CG_TOOL_ROOT}` and similar placeholders in `system_headers` with values from `env_profile.resolved_vars`
2. Create or select the toolchain, depending on mode
   - **[Host toolchain]**: call `ct_list_host_toolchains()` to retrieve the existing host toolchain list
     - Reuse the selected toolchain's `toolchainId` directly (**no `ct_create_toolchain` call**)
     - Record the selection result under `host_toolchain`
   - **[Conversion toolchain]**: call `ct_create_toolchain(toolchainName, confFilePath, infoFilePath, iniFilePath, systemHeaders)` - `confFilePath` and `infoFilePath` must be **absolute paths**, and `iniFilePath` is **required**. Without it, the toolchain is registered as a host toolchain and analysis fails later.
   - Name: `{session_id}_{HHmmss}_tc` to avoid collisions
   - Capture `toolchainId` from the return value for later steps
   - Patch the returned `toolchainId` into the existing project payload temporary file with a serializer. Do not create another helper script just to inject the ID.
3. Call `ct_create_project` with **explicit `sourceFiles`**
   - Use the file list finalized in confirmation 1. Using only `sourceDir` can accidentally include AI-generated files.
   - Project name: `{session_id}_{HHmmss}_project`
   - `toolchainId`: the ID returned or selected in step 2
   - If this call fails, stop here. Do not record `ct_resources.project_name` or `status=project_created`, and do not bypass the failure with `ct_set_project_toolchain`, `ct_analyze`, or `ct_create_test`.
4. Call `ct_get_project_settings`; it must succeed before Phase 3 is complete.
   - Store only returned `workingDirectory` in `ct_resources.working_directory`.
   - Use `projectPath` and `sourceFiles` only as in-memory completion checks. Do not store them in state.
5. Call `ct_set_compile_flags` if `project_inputs` contains user includes or defines. Use only `-I` and `-D` forms
6. Deep-merge into `state.json` only after all completion conditions pass
   - In `conversion`, calculate fingerprints
   - In `host`, record `host_toolchain`

**Canonical source for compile flags**:
- Values passed to `ct_set_compile_flags` in Phase 3 must always come from `project_inputs.include_paths.user` and `project_inputs.defines`.
- `compiler_info.include_paths.system` and `env_profile.system_headers` are toolchain or system-header inputs. They are not the canonical source for `ct_set_compile_flags`.

**`compileFlags` type contract (must be a single string)**:
- The `compileFlags` parameter of `ct_set_compile_flags` is a **single whitespace-separated string**, as defined by the installed CT tool contract.
- A JSON array is rejected. This does not mean to reduce the array size; it means **send a string, not an array**.
- **Correct payload**:
  ```json
  { "projectName": "...", "compileFlags": "-I\"C:/path/inc\" -D__MSP430F5500__" }
  ```
- **Incorrect payload (rejected by Java)**:
  ```json
  { "projectName": "...", "compileFlags": ["-I\"C:/path/inc\"", "-D__MSP430F5500__"] }
  ```
- **PowerShell pitfall**: Building an array such as `@('-I"..."', '-D...')` and passing it to `ConvertTo-Json` produces a JSON array. Build a whitespace-separated `[string]` from the start.
  ```powershell
  $userIncludes = ($project_inputs.include_paths.user | ForEach-Object { "-I`"$_`"" }) -join ' '
  $defines      = $project_inputs.defines -join ' '
  $compileFlags = ($userIncludes, $defines | Where-Object { $_ }) -join ' '   # single string
  ```
- **Bash recommendation**: Build one string, for example: `compileFlags="$(printf -- '-I\"%s\" ' "${user_includes[@]}")$(printf '%s ' "${defines[@]}")"`.

**Forbidden**:
- Do not pass relative paths to conf or ini
- Do not mix user include paths into `systemHeaders`
- Do not include target-only flags such as `-vmsp` in `compileFlags`
- Do not use TI syntax such as `--include_path` in `ct_set_compile_flags`
- Do not pass `compileFlags` as a JSON array. `ct_set_compile_flags` accepts only a single string; build it as a single string before calling the tool.
- Do not use metadata `conf/ini/info` files directly without Phase 2. Metadata files are originals. Only use the outputs processed by Phase 2 (`conf_merger.py`) for the host environment, including corrected `toolchain_kind`

**Validation**: If this is an IDE project session and `project_inputs.defines` is empty, a device macro may be missing. Ask the user to confirm.

## Output Schema (fields added or updated in Phase 3)

Example `host` output:

```json
{
  "status": "project_created",
  "ct_resources": {
    "toolchain_id": "{selected host ID}",
    "toolchain_name": "{selected host toolchain name}",
    "project_name": "{session_id}_{HHmmss}_project",
    "working_directory": "{abs_csdata_path}"
  },
  "host_toolchain": {
    "toolchain_id": "{selected host ID}",
    "name": "{selected host toolchain name}",
    "selected_via": "ct_list_host_toolchains"
  }
}
```

Example `conversion` output:

```json
{
  "status": "project_created",
  "target_macros_path": "{abs_target_macros_path}",
  "compiler_info_path": "{abs_compiler_info_path}",
  "conf_path": "{abs_conf_path}",
  "artifacts": {
    "target_macros_path": "{abs_target_macros_path}",
    "compiler_info_path": "{abs_compiler_info_path}",
    "conf_path": "{abs_conf_path}",
    "meta_ini_path": "{abs_ini_path}",
    "meta_info_path": "{abs_info_path}"
  },
  "ct_resources": {
    "toolchain_id": "{ct_create_toolchain return ID}",
    "toolchain_name": "{session_id}_{HHmmss}_tc",
    "project_name": "{session_id}_{HHmmss}_project",
    "working_directory": "{abs_csdata_path}"
  },
  "fingerprints": {
    "conf_hash": "sha256:{16hex}",
    "ini_hash": "sha256:{16hex}"
  }
}
```

**Note**: `ct_resources` allows only the four fields above: `toolchain_id`, `toolchain_name`, `project_name`, and `working_directory`. Do not include `project_path`, `sourceFiles`, `project_settings_verified`, or `compile_flags`.
**Mode rules**:
- In `host` mode, record `host_toolchain` and do not create conversion-only fields such as `fingerprints` or new Phase 2 artifacts.
- In `conversion` mode, keep the Phase 2 artifacts (`target_macros_path`, `compiler_info_path`, `conf_path`, `artifacts.*`) and add `ct_resources` and `fingerprints`.
- Record `fingerprints` only in `conversion` mode. Hash values must include the `sha256:` prefix.

## Product-backed execution boundary

Name-collision handling, regression reruns, and state validation are supplied with the installed CT/DVERA environment. Use its canonical documentation when available. If it is unavailable, do not create or modify a CT project; summarize the resolved project inputs and direct the user to bizcenter@suresofttech.com.
