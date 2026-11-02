---
name: ct-make-conf
description: Use this skill to generate the conversion analysis `.conf` and toolchain metadata (`.ini`, `.info`) from extracted target macros and `compiler_info`, and to record fingerprints.
---

# /ct-make-conf - Analysis Environment Configuration (Phase 2)

**Primary request**: Use this skill when generating the conversion toolchain configuration files (`conf`, `ini`, `info`) from extracted macros and compiler info.

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

**Entry**: `status` is `macros_extracted` and `toolchain_mode=conversion`
**Input**: `state.json` -> top-level `target_macros_path`, top-level `compiler_info_path`, `compiler_info`, `conf_mapping` (`artifacts.target_macros_path` and `artifacts.compiler_info_path` are mirror or compatibility fields)
**Output**: `.conf` (and `.ini`, `.info` in metadata mode), `state.json` (`status=conf_generated`, `fingerprints`)
**Execution mode**: In-memory state when called through `ct-orchestrator` / one-time `state.json` read in standalone mode
**Standalone guard**: In standalone mode, read `state.json` and confirm that `status` is `macros_extracted`.
- If `state.json` is missing or `status` is not `macros_extracted` -> **stop immediately** and tell the user to run `ct-init-project` first to complete project preparation
- If `toolchain_mode` is `host` or unresolved -> **stop immediately** and tell the user that this phase runs only in conversion mode
- If the Phase 1 outputs are missing (top-level `target_macros_path`, top-level `compiler_info_path`, `compiler_info`, `conf_mapping`), conf generation cannot proceed

**Phase 1 path contract**:
- The current validator's canonical read contract uses top-level `target_macros_path` and `compiler_info_path`
- `artifacts.target_macros_path` and `artifacts.compiler_info_path` are still kept as mirror or compatibility fields in the cross-phase state contract
- In later phases, the canonical source of compile flags is `project_inputs`, while `compiler_info` remains the original conversion analysis record
- The single `source_info.language` chosen in Phase 1 is passed through to `conf_mapping.language`. Allowed values are only `"C"` and `"CPP"`; normalize `C++` to `"CPP"` and never use mixed state-language tokens such as `C_CPP` or `both`.

**Bootstrap variables** (acquired in Phase 0; end-to-end entry via `ct-init-project`, resume entry via `ct-orchestrator`):
- `{ctPython}`: Python executable path confirmed in Phase 0, based on `ct_get_env.pythonPath`
- `{ctTool}`: `ct_tool.py` execution path confirmed in Phase 0. Used for `ct_list_host_toolchains` in Linux
- `skillResourceRoot`: autoconfig path from `ct_get_env.skillResourceRoot`
- `metaDir`: metadata path from `ct_get_env.metaDir`
- `sessionsBase`: workspace base path from `{baseDir}/sessions/ (derived)`

## Shared File and Encoding Rules

- Read and write all text files using **UTF-8 without BOM** by default
- Python scripts must accept both BOM and no-BOM on read, and always write files as UTF-8 without BOM
- Apply this rule to phase output text files such as `state.json`, `compiler_info.json`, `observations.jsonl`, `.conf`, `.ini`, and `.info`
- Do not build JSON or JSONL by concatenating strings. Always use serializers such as `json.dump` or `json.dumps`
- When exchanging JSON or text through process `stdout`, `stderr`, pipes, or redirects, handle everything as UTF-8
- In PowerShell, set `$env:PYTHONIOENCODING="utf-8"` before running Python tools directly. This avoids CP949 decoding delays when metadata matching failures emit Korean stderr.
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

**Core sequence**:
1. Load input from `state.json` and ask the user if it is missing
   - This phase is `conversion`-only. Do not run it in `host` mode
2. Select the host GCC (**choose from bundled templates only - do not search system GCC**):
   - **Windows**: extract the version from target macros such as `__VERSION__` or `__GNUC__`, then choose the closest higher version among the built-in template candidates 4.7, 5.3, and 9.5. Those three are the full set. There is no need to search the system
   - **Linux**: CT has no default bundled host GCC. Call `{ctPython} {ctTool} call ct_list_host_toolchains --json "{}"` to list host toolchains, obtain the GCC version and conf path, and use that conf as the host template for `conf_merger.py`
3. Confirm template existence under the installed `{skillResourceRoot}` returned by `ct_get_env` -> **Path A** (`{skillResourceRoot}/engine/conf_merger.py`) or **Path B** (manual assembly)
4. Path A: `{ctPython} {skillResourceRoot}/engine/conf_merger.py -t {macros} --os {OS} --lang {C|CPP} --ver {host_gcc} --std {std} -o {out}`
   - Metadata mode: `--meta-dir {metaDir} --compiler-info {info} --compiler-type {type} --vendor {conf_mapping.vendor} --compiler-name {conf_mapping.compiler_name} --arch {conf_mapping.target} --compiler-version {conf_mapping.version} --lang {language}`
   - In metadata mode, pass the vendor/compiler-name/arch/compiler-version values resolved in `conf_mapping` explicitly. Do not rely on `compiler_info` fallback. `--arch` is the CSV target key (`MSP430`, `ARM`, etc.), not an MCU or ISA variant such as `MSP430X`.
   - `--lang` must come from the Phase 1 single-language value. Do not rescan source extensions or infer the language again in Phase 2.
4.5. **ini resolve** (required): in metadata mode, `conf_merger` copies it automatically. In **legacy mode**, resolve it separately with `{skillResourceRoot}/engine/meta_loader.py` using canonical guidance from the installed CT/DVERA environment.
4.6. **Validate `toolchain_kind`** (required): confirm that the copied ini's `toolchain_kind` matches the selected host GCC version. Correct it when mismatched:
   - **Windows** mapping: `4.7->47`, `4.9->49`, `5.3->53`, `9.5->95`
   - **Linux** mapping (64bit suffix required): `4.7->47_64`, `4.9->49_64`, `5.3->53_64`, `9.5->95_64`, `11.5->115_64`
   - Metadata ini originals often contain stale `toolchain_kind` values, so you must validate this field
5. Validate the conf (target options, duplicate macros, whitelist)
6. Deep-merge into `state.json` (top-level `conf_path`, `host_gcc`, `artifacts.conf_path`, `artifacts.meta_ini_path`, `artifacts.meta_info_path`, `fingerprints`). **All paths must be absolute**

**CT function**: `ct_list_host_toolchains()` - used on Linux to retrieve host GCC version and conf path. Not needed on Windows
- Actual execution form:
  ```bash
  {ctPython} {ctTool} call ct_list_host_toolchains --json "{}"
  ```
- **Return**: `{ totalCount, toolchains: [{ id, cCompilerPath, cConfFilePath, cppCompilerPath, cppConfFilePath }] }`
- Extract the GCC version from `cCompilerPath` or `cppCompilerPath`, and use `cConfFilePath` or `cppConfFilePath` as the host template for `conf_merger.py`

**Forbidden**:
- **Do not search system GCC on Windows**. No `gcc --version`, `which gcc`, PATH search, or anything similar. Select host GCC only from the installed product templates under `{skillResourceRoot}/data/templates/Windows/` (4.7, 5.3, 9.5). The system does not need a separately installed GCC
- **Do not read conf_merger.py source to infer host information**. `conf_merger.py` is a tool that receives the host version through `--ver`; it is not a host-environment discovery tool
- Do not pass the target compiler version to `--ver`. Use only the host GCC version
- Do not hand-convert hundreds of macros. Always use the script
- In metadata mode, do not let AI guess `#NAME` or `#ID`. Use only the script matching result
- **Never let AI create the `.ini` file directly**. Use only the file automatically copied from metadata by `{skillResourceRoot}/engine/conf_merger.py`
- **For `toolchain_kind`, only host GCC version mapping correction is allowed**. Do not assign arbitrary values. Only correct it using the OS-specific mapping table in step 4.6. Linux requires the `_64` suffix
- **Do not reference `{metaDir}/legacy/`**. Old paths contain mismatched values such as stale `toolchain_kind`. Always use `{metaDir}/{Vendor}/{Compiler}/`
- **Even in Path B, `.ini` still requires metadata resolve**. Assemble only the conf manually. Resolve ini with `{skillResourceRoot}/engine/meta_loader.py`. If resolve fails, report it to the user
- **Do not fall back to host GCC metadata (`{metaDir}/FreeSoftware/gcc/*`) as `.ini`/`.info` source in `conversion` mode**. Host GCC metadata registers the toolchain as a host toolchain in Phase 3 `ct_create_toolchain`, which completely breaks conversion. The `.conf` file uses a host GCC **template** (for macro merging), but the `.ini`/`.info` pair **must** come from the target vendor directory (`{metaDir}/{Vendor}/{Compiler}/`). If target vendor metadata cannot be resolved, stop and ask the user. Never substitute with `FreeSoftware/gcc`.
- **Before calling `meta_loader.find_best_match`, always translate `conf_mapping.compiler_name` through `COMPILER_TYPE_TO_VENDOR`**. Do not pass raw executable names like `cl430`, `armcc`, or `arm-none-eabi-gcc`. The CSV stores normalized compiler column values (`Compiler`, `gcc`, `DS5-armcc`, ...). Mismatches return `NO_MATCH`, which tempts AI into the forbidden host-GCC fallback above.
- In metadata-mode `conf_merger.py` calls, do not omit `--vendor`, `--compiler-name`, `--arch`, or `--compiler-version`. Assuming `--compiler-info` plus `--compiler-type` is enough can reintroduce `NO_MATCH` when `target_arch` differs from the CSV target key.

**Role separation (conversion mode)**: the two artifact families serve different roles. Do not mix them up.

| Artifact | Role | Source |
|----------|------|--------|
| `.conf` | Macro set consumed by analysis preprocessor | Target macros (Phase 1) + **host GCC template** from `{skillResourceRoot}/data/templates/Windows/gcc_{ver}/` |
| `.ini` / `.info` | Metadata that registers the toolchain as a **conversion** toolchain | **Target vendor metadata** at `{metaDir}/{Vendor}/{Compiler}/{Vendor}_{Compiler}_{Version}_{Target}_{HostOS}_{Language}.{ini,info}` |

If metadata matching selects a CSV entry whose language is `C_CPP`, that value is only the metadata entry key and may appear in the selected file basename. State language fields still store only `"C"` or `"CPP"`.

## Output Schema (fields added or updated in Phase 2)

```json
{
  "status": "conf_generated",
  "target_macros_path": "{abs_target_macros_path}",
  "compiler_info_path": "{abs_compiler_info_path}",
  "conf_path": "{abs_conf_path}",
  "host_gcc": {
    "version": "5.3",
    "os": "Windows|Linux",
    "template_path": "{skillResourceRoot}/data/templates/... or the conf path returned by ct_list_host_toolchains on Linux",
    "selection_reason": "target EDG gcc X.X -> host Y.Y"
  },
  "artifacts": {
    "target_macros_path": "{abs_target_macros_path}",
    "compiler_info_path": "{abs_compiler_info_path}",
    "conf_path": "{abs_conf_path}",
    "meta_ini_path": "{abs_ini_path}",
    "meta_info_path": "{abs_info_path}"
  },
  "fingerprints": { "conf_hash": "sha256:{16hex}" }
}
```

**Note**: `host_gcc` must be an object. Do not use a string such as `"5.3"`. `fingerprints.conf_hash` must include the `sha256:` prefix.
**Retention rule**: The Phase 2 state must keep the Phase 1 top-level `target_macros_path` and `compiler_info_path`. `validate_phase2()` still reads those locations directly
**Mirror rule**: `artifacts.target_macros_path` and `artifacts.compiler_info_path` are mirrors for JSON example alignment and downstream phase compatibility
**Required**: `artifacts.meta_ini_path` **must be set**. If it is missing, `ct_create_toolchain` in Phase 3 registers the result as a host toolchain and analysis fails. In metadata mode, `conf_merger.py` copies it automatically. In legacy mode, resolve it separately in step 4.5
**Required**: `artifacts.meta_info_path` **must also be set**. `ct_create_toolchain` now requires `infoFilePath`. The `.info` file is located in the same metadata directory as the `.ini` file, for example `{Vendor}_{Compiler}_{Version}_{Target}_{HostOS}_{Language}.info`

## Product-backed execution boundary

Host overrides, compiler corrections, metadata naming, and legacy ini resolution are supplied with the installed CT/DVERA environment. Use its canonical documentation when available. If it is unavailable, do not generate or modify CT configuration artifacts; report the prepared inputs and direct the user to bizcenter@suresofttech.com.
