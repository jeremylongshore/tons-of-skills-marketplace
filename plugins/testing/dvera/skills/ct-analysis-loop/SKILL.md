---
name: ct-analysis-loop
description: Use this skill during the CT project analysis phase to classify errors, repeat conf or toolchain fixes, and continue until analysis succeeds.
---

# /ct-analysis-loop - Source Code Analysis (Phase 4)

**Primary request**: Use this skill when repeating configuration fixes and re-analysis after an analysis failure, or when recording `functions_found` in state.

**Entry**: `status` is `project_created`
**Input**: `state.json` -> `ct_resources.*` + (for `conversion`, top-level `conf_path`; keep `artifacts.conf_path` as a mirror)
**Output**: `state.json` (`status=analysis_success`)
**Execution mode**: In-memory state when called through `ct-orchestrator` / one-time `state.json` read in standalone mode
**Standalone guard**: In standalone mode, read `state.json` and confirm that `status` is `project_created`.
- If `state.json` is missing or `status` is not `project_created` -> **stop immediately** and tell the user to run `ct-init-project` first to complete project preparation
- If Phase 3 outputs (`ct_resources.project_name`, `ct_resources.working_directory`) are missing, analysis cannot proceed
- In `conversion`, if top-level `conf_path` is missing or the `artifacts.conf_path` mirror is not kept with it, treat it as a Phase 2/3 regression target
**conf path contract**:
- The canonical input in the cross-phase state contract is top-level `conf_path`
- Under the current runtime or validator contract, `artifacts.conf_path` must also be kept, and both values must point to the same absolute path
**Precondition**: Use the bootstrap variables acquired in Phase 0. In end-to-end entry, `ct-init-project` prepares them. In resume entry, `ct-orchestrator` prepares them. Even in standalone mode, run the bootstrap procedure below first.

## Shared File and Encoding Rules

- Read and write all text files using **UTF-8 without BOM** by default
- Python scripts must accept both BOM and no-BOM on read, and always write files as UTF-8 without BOM
- Apply this rule to phase output text files such as `state.json`, `compiler_info.json`, `observations.jsonl`, `.conf`, `.ini`, and `.info`
- Do not build JSON or JSONL by concatenating strings. Always use serializers such as `json.dump` or `json.dumps`
- When exchanging JSON or text through process `stdout`, `stderr`, pipes, or redirects, handle everything as UTF-8
- Minimize inline execution such as `python -c`. When paths, JSON, and Python code are nested in one string, encoding and escaping failures become much more likely
- Store paths written into `state.json`, JSON payloads, and logs or metadata as **absolute paths**, and normalize to `/` when it is safe to do so
- Do not force blanket `/` normalization for paths passed to external process `argv`. Use `argv` lists by default, and only use `/` normalization when the target tool is known to accept it safely
- Use `LF` as the default line ending for newly created internal management files such as `state.json`, `compiler_info.json`, and `observations.jsonl`. Preserve existing line endings when editing an existing file
- Do not rewrite existing artifacts only for encoding normalization. Unnecessary rewrites can change fingerprints
- Build JSON payloads with a serializer-backed temporary file by default. Prefer Python `json.dump(..., ensure_ascii=False)` with `tempfile.NamedTemporaryFile(delete=False, encoding="utf-8")` or `tempfile.gettempdir()`, then pass it as `ct_tool.py call ... --json "@{path}"`.
  - Do not hand-escape path strings. Let the JSON serializer handle Windows backslashes and non-ASCII text.
  - Use `@-` stdin only as a secondary input channel.
  - PowerShell `ConvertTo-Json` is a Windows-only auxiliary option; Bash heredoc/cat examples must not be the default payload path.
- Even for simple payloads, prefer a temporary JSON file or `argv` lists over one-line string payloads.

## Execution Guardrails

- **Do**:
  - Record exactly one attempt object per loop iteration in `analysis_loop.attempts[]`
  - Keep `modifications` as an array at all times, and when an attempt succeeds, write `functions_found` **inside the last successful attempt object**
  - If you intentionally modify the conf in `conversion`, update `fingerprints.conf_hash` immediately in the same attempt
  - Read only high-priority log files in a limited scope, and confirm whether anything changed from the previous attempt before repeating the same diagnosis
  - On the first diagnostic pass, query only `log/pa/PA_*.log`, `log/parse/*.elog`, and `log/preprocess/*.plog`
- **Do not**:
  - Record `functions_found` at the top level or directly under `analysis_loop`
  - Read full log bodies, or combine high-risk edits with other edits in the same attempt
  - Run `Get-ChildItem -Recurse` over the whole working directory on the first failure diagnostic
  - Load broad diagnostic guidance before the current evidence requires it
  - Repeat the same edit and the same diagnosis back-to-back
  - Call `ct_set_project_toolchain` again after `ct_modify_toolchain`
- **Why**:
  - The Phase 4 attempt record is shared by the validator, fingerprint resume decisions, Phase 5 input, and kb-update observation collection
- **Stop and Ask summary**:
  - If the same regression reason repeats twice, stop and escalate to the user.
  - If a high-risk conf edit such as `cs_replace_code` is required, or if phase regression is needed, stop and reconfirm the decision.
  - If `functions_found == 0` but the source likely contains real function definitions, do not mechanically finalize the result without rechecking.
- **Safe pattern**:

```json
{
  "attempt": 2,
  "result": "success",
  "functions_found": 12,
  "error_lines": [],
  "modifications": []
}
```

## Pre-Work Gate Check

1. In `conversion`, confirm that top-level `conf_path` and the `artifacts.conf_path` mirror point to the same absolute path
2. Fix the minimum fields of the current `attempt` object first: `attempt`, `result`, `error_lines`, `modifications`
3. If you plan to edit conf, decide in advance whether you will update `conf_hash` within the same attempt
4. Decide the priority and maximum read range of log files before starting

**Standalone bootstrap procedure**:
1. If `bootstrap.ct_home` exists in `state.json`, use that value.
   - However, if either condition below fails, treat it as **invalid** and fall back to one-time OS-specific default installation path checking.
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
4. Call `ct_get_env` to acquire `pythonPath`, `skillResourceRoot`, `toolRoot`, `metaDir`, and `baseDir`
   ```bash
   {ctPython} {ctTool} call ct_get_env --json "{}"
   ```
5. Normalize `ctPython`, `ctTool`, and `skillResourceRoot` from the returned values
6. Once `sessionsBase` is known, search for the latest session's `state.json` under `{sessionsBase}/`
   - If there are multiple sessions, show the list and ask the user to choose

**Bootstrap variables** (acquired in Phase 0; end-to-end entry via `ct-init-project`, resume entry via `ct-orchestrator`, or by the standalone procedure above):
- `{ctPython}`: Python executable path based on `ct_get_env.pythonPath`
- `{ctTool}`: `ct_tool.py` execution path
- `skillResourceRoot`: autoconfig path from `ct_get_env.skillResourceRoot`
- `metaDir`: metadata path from `ct_get_env.metaDir`
- `sessionsBase`: workspace base path from `{baseDir}/sessions/ (derived)`

**CT functions** (used in Phase 4):
- `ct_analyze(projectName)` - run analysis
- `ct_get_functions(projectName)` - fetch the function list on success
- `ct_modify_toolchain(toolchainId, confFilePath?, confType?, systemHeaders?, language?)` - apply conf or header changes. **After this call, do not call `ct_set_project_toolchain`**. Reflect the change by rerunning `ct_analyze`
- `ct_set_compile_flags(projectName, compileFlags)` - adjust flags
- `ct_get_toolchain(toolchainId)` - retrieve the current toolchain settings for rollback

**Language contract**:
- Phase 4 reuses the `"C"` or `"CPP"` value from `state.source_info.language`.
- When sending `confFilePath` to `ct_modify_toolchain`, also send `confType` as `"C"` or `"CPP"`.
- When sending `systemHeaders`, also send `language` as `"C"` or `"CPP"`.
- If the tool returns `INVALID_PARAMS`, do not guess. Ask the user to choose `1) C  2) CPP`, retry at most once, and stop Phase 4 if it still fails.
- ini-only calls (`iniFilePath`) are unaffected by `confType` or `language`.

**Core sequence**:
1. Initialize: load input, back up the conf original as `.original` in `conversion`, and save the initial state
2. Run `ct_analyze`:
   - If `ct_analyze` returns `success=true` **and** `ct_get_functions` returns a non-empty list -> write `functions_found=N` in the successful attempt and exit
   - If `ct_analyze` returns `success=true` **but** `ct_get_functions` returns 0 functions **while** `source_info.file_count >= 1` and at least one source file contains a real function definition (grep for `^\w[\w\s*]*\(.*\)\s*\{` or an equivalent C function-body pattern) -> **treat this as a Phase 4 failure**, not a success. Run the `functions_found=0 recovery checklist` below before starting a retry attempt
3. On failure, run the loop (up to 5 attempts):
   a. Collect errors from category-specific logs:
      - PA analysis, system headers, memory: `log/pa/PA_*.log`
      - Parse errors: `log/parse/*.elog` (exists only on failure)
      - Preprocess errors: `log/preprocess/*.plog` (exists only on failure)
      - Preprocess result diagnostics: `log/fe/.work/preprocess/*.i`
      Use limited extraction with PowerShell `Select-String` + `Select-Object -First N` or an equivalent bounded `grep + head` pattern
      Keep the first lookup to those patterns only; do not recursively list the whole working directory.
   b. Classify errors by priority: infrastructure > memory > **system headers** > preprocessing > conf-symbol
   c. Apply fixes: edit conf -> `ct_modify_toolchain` with `confType`/`language` -> `ct_analyze` rerun / or update `compileFlags`
   d. Judge progress: improved (15% decrease), stalled, or regressed (10% increase) -> rollback up to 2 times

**Fingerprint rules**:
- If you intentionally modify the conf in `conversion`, recalculate `fingerprints.conf_hash` immediately within the same attempt
- Once called, the fingerprint helper always recalculates against the current conf file. The responsibility for deciding whether to call the helper belongs to this Phase 4 orchestration logic
- `host` mode does not enforce conf or ini fingerprints

**Single-change recording rules**:
- Always store `modifications` as an array for each attempt
- **Only when there is exactly one modification**, record `detail`, `diagnosis`, and `intent` inside `modifications[0]`
- `detail` is the required string for observation-record collection
- If there are 2 or more modifications, do not record `diagnosis` or `intent`
- `verdict=improved/stalled/regressed` is later used by `ct-kb-update` to build positive or negative observation records

**Product guidance loading**: After the first failure, use the canonical diagnostic guidance supplied by the installed CT/DVERA environment when available. If it is unavailable, do not guess a product-specific recovery action; report the evidence collected so far and stop.

**Quick reference** (always use the ref documents as the actual decision basis):
- `identifier "X" is undefined` + keyword -> `cs_ignore_single_keyword=X`
- `identifier "X" is undefined` + type -> `cs_builtin_declaration=typedef ... X;`
- `could not open source file` + system header -> add `ct_modify_toolchain(systemHeaders, language=source_info.language)`
- `could not open source file` + project header -> add `-I` through `ct_set_compile_flags`

**Phase regression**: setting application failure -> P3, conf root cause -> P2, polluted macros -> P1, same reason twice -> user escalation

**Forbidden**:
- Do not read full large logs. Always use bounded extraction such as PowerShell `Select-String` + `Select-Object -First N`
- Do not combine high-risk edits such as `cs_replace_code` with other edits in the same attempt
- Do not repeat the same edit
- Do not misclassify assertion failures as environment issues
- **Do not call `ct_set_project_toolchain` after `ct_modify_toolchain`**. Reflect toolchain edits by rerunning `ct_analyze`
- **Do not paper over Phase 1/2 gaps by hand-patching the conf in Phase 4.** If the analysis failure is rooted in missing or wrong target macros (e.g., `#error "Failed to match a default include file"` inside a vendor system header), the fix belongs in a Phase 1/2 regression - rerun `ct-extract-macro` with the correct dump flag, regenerate conf, then retry analysis. Injecting `cs_define_macro_name=__TARGET_MCU__=1` directly into Phase 2 output to get past the symptom is forbidden; it hides the root cause and corrupts the observation record for `ct-kb-update`.
- **Do not silently work around CT tool errors by switching to direct artifact edits.** If a tool returns a structured input or type error, **stop** and report the failed operation and payload shape. Do not invent a workaround such as inlining flags into the conf file; that corrupts both fingerprints and the Phase 2 canonical input contract.

## `functions_found=0` Recovery Checklist

When `ct_analyze` returns success but `ct_get_functions` yields 0 functions, and the source clearly contains function definitions, do **not** finalize the phase. Work through the checklist below in order and record the finding in `error_lines` for the next attempt.

1. **Source has real functions?** Grep the source for function-body patterns. If the source truly has none (pure header/data file), finalize with `functions_found=0` legitimately. Otherwise continue.
2. **Preprocessed output was stripped?** Check `{working_directory}/src/preprocessed/<name>_1.i.c` (or `obj/<name>.c.*/src/preprocessed/`). If the file is suspiciously small (for a non-trivial source, under ~30 lines often means every `#include` collapsed to nothing), the root cause is typically a missing target-MCU or vendor macro - the vendor's device header hit its fall-through `#error` and stopped expansion.
3. **Target macros match the real compiler?** Compare `target_macros.txt` line count to what the real compiler would emit. Real dumps from GCC/Clang/cl430/iccarm typically produce 40~200+ entries. If your `target_macros.txt` has ~15 entries and lacks `__VERSION__`, `__EDG_VERSION__`, `__TI_COMPILER_VERSION__`, or the equivalent, **Phase 1 is the root cause** - regress to Phase 1 and use the compiler's documented macro-dump command. Do not patch the conf here.
4. **Preprocessor `.plog` has `ERROR2007` / `#error` / `catastrophic error`?** Read the `.plog` for the failing source with bounded extraction. A catastrophic error at line N of a vendor header (e.g., `msp430.h`, `stm32f4xx.h`) that says `"Failed to match a default include file"` is **definitive evidence of missing target macros** - regress to Phase 1.
5. **System headers are actually on disk and readable?** Verify each `env_profile.system_headers` path exists and contains real header files (`ls {path}/*.h | head`). A system header path that exists but is empty is a Phase 1 header-collection bug.

**Phase regression decision matrix for `functions_found=0`:**

| Checklist finding | Regression target | Reason |
|-------------------|-------------------|--------|
| `target_macros.txt` missing `__VERSION__`/vendor version macros | **Phase 1** | dump flag was wrong or macros were hand-written |
| `.plog` shows `"Failed to match a default include file"` | **Phase 1** | target-MCU macro missing from dump |
| `env_profile.system_headers` path exists on disk but contains no headers | **Phase 1** | header-collection logic picked the wrong directory |
| Preprocessed `.i` is near-empty but macros and system-header contents look correct | Phase 2 or 3 | conf merge or `systemHeaders` wiring |
| Source genuinely has no functions | Finalize | `functions_found=0` is a legitimate result |

## Output Schema (fields added or updated on Phase 4 success)

```json
{
  "status": "analysis_success",
  "analysis_loop": {
    "attempt_count": 2,
    "max_attempts": 5,
    "loop_epoch": 1,
    "attempts": [
      {
        "attempt": 1,
        "result": "failed",
        "verdict": "stalled",
        "error_lines": ["identifier \"__packed\" is undefined"],
        "modifications": [
          {
            "action": "conf_add",
            "detail": "cs_define_macro_name=__packed",
            "diagnosis": "__packed is an undefined compiler extension keyword in the host environment",
            "intent": "Define it as an empty macro so it is ignored"
          }
        ]
      },
      {
        "attempt": 2,
        "result": "success",
        "functions_found": 12,
        "error_lines": [],
        "modifications": []
      }
    ]
  }
}
```

**Note**: Do not turn `attempt_count` into a separate object like `{"phase1":1,"phase2":1,...}`. It must stay inside `analysis_loop`.
**Minimum validator contract**:
- `analysis_loop` must contain `attempt_count`, `loop_epoch`, and `attempts[]`
- If `verdict` is recorded, the only allowed values are `improved`, `stalled`, and `regressed`
- If `modifications` length is 1, `modifications[0]` must be an object, and `detail`, `diagnosis`, and `intent` must be non-empty strings
**Required location**: Record `functions_found` inside the **last successful attempt object** in `analysis_loop.attempts[]`. Do not place it at the top level or directly under `analysis_loop`.
**Documentation convention**: Keep `attempt`, `result`, `error_lines`, and `modifications` in example JSON. For multi-change attempts, keep only the `modifications` array and omit `diagnosis` and `intent`.

## Product-backed execution boundary

Detailed recovery rules and state validation are supplied with the installed CT/DVERA environment. Use its canonical documentation when available. If it is unavailable, do not guess or execute product-specific recovery steps; collect the inputs and evidence, explain the intended workflow, and direct the user to bizcenter@suresofttech.com.
