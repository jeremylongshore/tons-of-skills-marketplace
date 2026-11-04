---
name: ct-extract-macro
description: Use this skill to extract the target compiler's compiler-default macros and build the shared environment analysis fields used during CT project preparation.
---

# /ct-extract-macro - Environment Analysis and Macro Extraction (Phase 1)

**Primary request**: Use this skill when rerunning macro extraction and shared environment analysis in Phase 1, or when correcting the `toolchain_mode` decision.

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

**Entry**: `status` is `pending` or missing
**Input**: User source project path
**Output**: pre-Phase3 state when `host` is confirmed, or `target_macros.txt`, `compiler_info.json`, and `state.json` (`status=macros_extracted`) when `conversion` is confirmed
**Execution mode**: In-memory state when called through `ct-orchestrator` / one-time `state.json` read in standalone mode

**Bootstrap variables** (acquired in Phase 0; end-to-end entry via `ct-init-project`, resume entry via `ct-orchestrator`):
- `{ctPython}`: Python executable path confirmed in Phase 0, based on `ct_get_env.pythonPath`
- `{ctTool}`: `ct_tool.py` execution path confirmed in Phase 0. This phase does not invoke CT product functions, but it keeps the same bootstrap contract.
- `skillResourceRoot`: autoconfig path from `ct_get_env.skillResourceRoot`
- `metaDir`: metadata path from `ct_get_env.metaDir`
- `sessionsBase`: workspace base path from `{baseDir}/sessions/ (derived)`

## Critical Pre-Work Checks

- For the `conversion` path, Phase 1 must populate both `env_profile.resolved_vars` and `env_profile.system_headers`.
- `env_profile.system_headers` must be a **non-empty list**. It is not a hidden input that can be postponed until Phase 3.
- The `system_headers=[]` example in the `host` path is for host mode only. Copying it into `conversion` will fail validation.
- `source_info.language` is always the single value `"C"` or `"CPP"`. If both C and C++ sources are detected, do not infer automatically; ask the user which language project to create first, then write only the selected single value into state and `compiler_info.language`.

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

**Temporary test workspace**: `{sessionsBase}/{session_id}/`

**Core sequence**:
1. Initialize the workspace at `{sessionsBase}/{session_id}/`
2. Collect source files -> record `source_info.source_paths` **(required - used in Phase 4/5)**, decide one language, and build the initial `project_inputs`
   - If only `.c` files are present, write `source_info.language = "C"`. If only `.cpp`/`.cc`/`.cxx` files are present, write `source_info.language = "CPP"`.
   - If both C and C++ sources are present, ask the user `1) C project first  2) CPP project first`. Interpret `1`/`C`/`c` as `"C"` and `2`/`CPP`/`C++`/`cpp` as `"CPP"`.
   - Do not automatically create the second-language project in this session. The user runs a separate init after finishing the first project.
3. **Analyze the project and decide `toolchain_mode`** - always before compiler discovery
   - If `state.json.init_inputs.toolchain_mode_preference` is present, adopt that value as `toolchain_mode` and do not ask the user again. Record the reason in `toolchain_mode_evidence` as "init_inputs preset".
   - Auto-discover project files such as `.cproject`, `*.uvprojx`, `*.ewp`, `*.vcxproj`, `compile_commands.json`, and `Makefile`
   - Parse them to identify compiler type and version, target, `-D`, `-I`, and build flags
   - If you see general PC project evidence such as `.vcxproj`, `Makefile`, `compile_commands.json`, `gcc`, `clang`, or `cl`, and there is no evidence against conversion, treat it as a `host toolchain candidate`
   - If it is a `host toolchain candidate`, explain the basis briefly and ask the user to confirm (skipped when the init_inputs preset rule applies)
   - When `host` is confirmed, write only `toolchain_mode`, `toolchain_mode_evidence`, `toolchain_mode_user_confirmed=true`, `source_info`, and `project_inputs`, then hand off to Phase 3. In this case keep `status` as `pending`
   - If the user rejects the `host toolchain candidate`, stop the current orchestration flow and do not temporarily store `host` without an answer
   - If IDE variables such as `${CCS_BASE_ROOT}` or IDE installation clues are found, first confirm whether a **single real path can be resolved only from project-root information**
   - If it is an IDE project and the path is still unresolved, **ask the user for the IDE installation root and do not continue until they answer**
4. **Discover the compiler and extract macros** - only for `conversion`, based on the Step 3 analysis result
   - Dump macros **only when a single compiler binary path is fully resolved** from identified compiler information or the IDE root
   - A bare executable name such as `gcc`, `clang`, `cl`, or `arm-none-eabi-gcc` does **not** mean the compiler path is resolved
   - Use **only an empty file (`/dev/null` or `NUL`) as input**, while preserving architecture and standard flags
   - **MANDATORY**: if the detected compiler is `cl430` (TI), `armcc`/`armclang` (Keil/ARM), `iccarm` (IAR), or `cl` (MSVC), consult the compiler documentation or canonical guidance supplied by the installed CT/DVERA environment **before** attempting any dump. These compilers do not use the GCC-style `-dM`/`-dD`/`--predefine` flags.
   - **Minimum dump-flag cheatsheet** (confirm encoding and empty-file handling in the compiler documentation):

     | Compiler | Dump invocation (empty file as input) |
     |----------|---------------------------------------|
     | GCC / Clang | `{cc} {flags} -dM -E -x c /dev/null > target_macros.txt` (Windows: use `NUL`) |
     | TI `cl430` | `cl430 {flags} --preproc_macros=target_macros.txt {empty.c}` |
     | IAR `iccarm` | `iccarm {flags} --predef_macros target_macros.txt {empty.c}` |
     | MSVC `cl` | `cl {flags} /E /d1PP {empty.c}` (parse stdout) |

     For other compilers in the same families (TI `armcl`, IAR `iccrl78`/`iccrx`, ARM `armcc`/`armclang`, etc.), **do not assume the flag above applies**. Consult installed product guidance or ask the user for the correct dump command before proceeding.

   - If the compiler path is unresolved or the binary does not exist, ask for the IDE installation root for IDE projects, or ask for the compiler path or build command for non-IDE projects, and do not enter metadata mode until the user answers
   - **If the dump flag is unknown or the dump command fails**: do **not** hardcode macros from memory or the project file. Consult installed product guidance; if still unresolved, ask the user for the correct dump command. See Forbidden below
5. For `conversion`, normalize `compiler_info.json` and auto-decide `conf_mapping` (`target`, `version`, `language`). Keep `compiler_info.language` aligned with the single language chosen in Phase 1. In metadata mode, align `compiler_info.target_arch` and `conf_mapping.target` to the same CSV target key, such as `MSP430`; do not use ISA or MCU variant names such as `MSP430X`.
6. Create `state.json` by deep-merge. **Store all paths as absolute paths**

**CT functions**: None. Call the local compiler directly.

**Forbidden**:
- Do not use source files as macro dump input because headers will contaminate the extracted macro set
- Do not leave behind a temporary empty file such as `ct_ai_empty.c` after extraction
- Do not arbitrarily edit macro kinds or values with AI. **Adjusting values inside a metadata macro file (`.macro`) for a version is also arbitrary modification**
- **Do not hardcode, guess, or hand-write `target_macros.txt` entries when the dump command fails or the correct flag is unknown.** Hand-written macros almost always miss critical entries like `__VERSION__ "EDG gcc X.Y mode"` (needed by `conf_merger.py` for host-GCC selection) and often use the wrong numeric format for `__TI_COMPILER_VERSION__`, `__EDG_VERSION__`, etc. Real dumps typically produce 40~200+ macros; a hand-written list of 10~20 entries is an immediate red flag. Use installed product or compiler guidance; if that does not resolve it, **stop and ask the user** for the correct dump command. Never fabricate the file to continue the pipeline.
- **Do not guess dump behavior for TI / IAR / ARM-Keil / MSVC compiler families.** The cheatsheet covers only a small set of binaries and is not a substitute for compiler or installed product guidance.
- In `compiler_info.json`, the version key must be `"compiler_version"` **not** `"version"` because `"version"` breaks metadata matching
- Do not use a host compiler as a substitute for the target compiler. In cross or embedded projects, extracting macros with host GCC creates a completely different architecture macro set and breaks the whole pipeline later
- Do not search default installation paths or known paths outside the project root. Do not guess IDE or compiler locations by scanning places such as `C:/ti`, `Program Files`, or `$HOME`
- Do not treat a bare executable name as a confirmed `compiler_path`. If project information alone cannot resolve a single real path, keep it unresolved
- Do not invent a fallback when the target compiler cannot be found. Ask for the IDE installation root first for IDE projects, and ask for the compiler path or build command for non-IDE projects
- Do not continue while IDE variables such as `${CCS_BASE_ROOT}` remain unresolved. Auto-resolve only values that can be resolved directly from the project root, such as `${PROJECT_ROOT}`. For everything else, ask for the IDE installation root and resolve it before continuing. Never use `"unknown"`
- **Do not record executable names (`cl430`, `armcc`, `iccarm`, `arm-none-eabi-gcc` and so on) in `conf_mapping.compiler_name` or `conf_mapping.vendor`**. Those fields must use the canonical vendor and compiler names returned by the installed CT/DVERA environment. If no canonical mapping is available, stop instead of falling back to host GCC metadata.
- **In metadata mode, do not let `compiler_info.target_arch` diverge from `conf_mapping.target`**. Both fields must use the target column spelling from `parserconfig.description.csv`. Preserve device or ISA variants elsewhere, but do not use them as Phase 2 matching keys.

## Output Schema (state.json at Phase 1 completion)

An example for the `conversion` path:

```json
{
  "session_id": "{YYYYMMDD}_{project}",
  "toolchain_mode": "conversion",
  "status": "macros_extracted",
  "workspace": "{abs_workspace_path}",
  "source_info": {
    "source_dir": "{abs_path}", "source_paths": ["{abs_path}", ...],
    "language": "C|CPP", "file_count": 1
  },
  "project_inputs": {
    "include_paths": { "user": ["{abs_path}", "..."] },
    "defines": ["-DDEBUG"]
  },
  "compiler_info_path": "{abs_path}/compiler_info.json",
  "target_macros_path": "{abs_path}/target_macros.txt",
  "conf_path": null,
  "conf_mapping": { "mode": "meta|target", "vendor": "...", "compiler_name": "...", "target": "...", "language": "C|CPP", ... },
  "env_profile": {
    "name": "ccs|iar|keil|generic",
    "confidence": "confirmed|fallback",
    "input_fingerprint": "sha256:{16hex}",
    "detected_by": ["project_file:.cproject", "compiler_binary:cl430.exe"],
    "resolved_vars": { "CG_TOOL_ROOT": "{abs_path}", ... },
    "system_headers": ["{abs_path}", "{abs_path}", "..."]
  },
  "artifacts": {
    "target_macros_path": "{abs_path}", "compiler_info_path": "{abs_path}"
  },
  "ct_resources": { "toolchain_name": null, "project_name": null },
  "analysis_loop": { "attempt_count": 0, "max_attempts": 5, "attempts": [] }
}
```

When a `host` candidate is confirmed, Phase 1 does not mark macro extraction as completed. It only stores the following pre-Phase3 state:

```json
{
  "session_id": "{YYYYMMDD}_{project}",
  "toolchain_mode": "host",
  "toolchain_mode_evidence": [".vcxproj detected", "compiler=cl"],
  "toolchain_mode_user_confirmed": true,
  "status": "pending",
  "workspace": "{abs_workspace_path}",
  "source_info": {
    "source_dir": "{abs_path}",
    "source_paths": ["{abs_path}", "..."],
    "language": "C|CPP",
    "file_count": 1
  },
  "project_inputs": {
    "include_paths": { "user": ["{abs_path}", "..."] },
    "defines": []
  }
}
```

This state is validated by the host pre-Phase3 branch in `validate_state.py phase=1`. Use `phase=3` validation only after `host_toolchain` and `ct_resources.*` are populated.

**Canonical Phase 1 locations**:
- The current validator reads top-level `target_macros_path` and `compiler_info_path` directly.
- `artifacts.target_macros_path` and `artifacts.compiler_info_path` are still kept as mirror or compatibility fields for the cross-phase state contract.

**Structure separation rules**:
- `project_inputs` is the shared canonical input that Phase 3 later passes to `ct_set_compile_flags`.
- `compiler_info.include_paths.system/user` preserves the original conversion analysis record and does not replace `project_inputs`.
- `source_info.language`, `compiler_info.language`, and `conf_mapping.language` use only `"C"` or `"CPP"`. Do not write mixed tokens such as `C_CPP`, `both`, or `Mixed` into state.
- In metadata mode, `compiler_info.target_arch` and `conf_mapping.target` must use the same CSV target key. For example, TI MSP430 families use `MSP430`; do not store `MSP430X` as the Phase 2 matching key.

**Notes**: Use `workspace` not `workspace_path`. Use `target_macros_path` not `macros_path`. Do not turn `attempt_count` into a structure like `{"phase1":1,...}`.
**Required (Phase 1 validator)**: `env_profile` must exist on the `conversion` path. `validate_state.py` validates `name`, `input_fingerprint` (with `sha256:` prefix), and `resolved_vars` (non-empty object) in Phase 1.
**Required (for the Phase 3 conversion contract)**: `env_profile.system_headers` must be a **non-empty list** already filled in Phase 1. Do not end Phase 1 without collecting IDE or SDK include paths.
**Resolution principle**: `system_headers` is the list of actual absolute paths for compiler or SDK system include directories resolved from `resolved_vars`. Use IDE/compiler documentation or canonical installed product guidance to collect them for CCS, Keil, IAR, or cross GCC.
**Optional**: If you record `env_profile` on the `host` path, use empty structures such as `resolved_vars={}` and `system_headers=[]`. Do not use `"unknown"` or empty strings.
**Host-only rule**: `system_headers=[]` is allowed only in `host`. In `conversion`, an empty list is not allowed.

## Product-backed execution boundary

IDE parsing, compiler-specific dump recipes, canonical vendor mapping, and state validation are supplied with the installed CT/DVERA environment. Use its canonical documentation when available. If it is unavailable, do not guess or fabricate compiler data; collect the project and compiler inputs, explain what remains unresolved, and direct the user to bizcenter@suresofttech.com.
