---
name: ct-kb-update
description: Use this skill to append single-change attempt results to `observations.jsonl`. It is called by `ct-init-project` or `ct-orchestrator` immediately after the CT-apply full pipeline completes.
---

# /ct-kb-update - Observation Record Collection Wrap-up Task

**Primary request**: Use this skill to append the results of single-change analysis and test attempts to `observations.jsonl`.

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

**Entry**: Called once immediately after end-to-end full-pipeline completion from `ct-init-project`, or after resume full-pipeline completion from `ct-orchestrator`
**Input**: Final in-memory state or `state.json`, `bootstrap.sessions_base`, `session_id`
**Output**: Append to `observations.jsonl`
**Nature**: Not a regular phase, best-effort, non-blocking
**Standalone guard**: This skill does not allow standalone execution. The official runtime entry point is the wrap-up task from `ct-init-project` (end-to-end entry) or `ct-orchestrator` (resume entry) that calls `{ctPython} {ctTool} kb-update --session-id "{session_id}"`.

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

This skill **persists the success or failure of single modifications from the feedback loop as observation records**.
It does not perform new reasoning. It only combines the already recorded `detail`, `diagnosis`, `intent`, `verdict`, and environment fields from `state.json` into JSONL records that match the design-document schema.

## Core Flow

1. Gather inputs
   - `analysis_loop.attempts[]`, `test_loop.attempts[]`
   - `session_id`
   - `bootstrap.sessions_base`
   - Each attempt's `attempt`, `verdict`, `modifications`, and `error_lines`
   - Environment fields such as `compiler_info`, `env_profile`, and `toolchain_kind`
   - For dedupe: `loop_kind`, `analysis_loop.loop_epoch`, and `test_loop.loop_epoch` from state
2. Compute the output path
   - Default path: `{sessionsBase}/observations.jsonl`
   - Do not place it under the session-specific path `{sessionsBase}/{session_id}`
3. Filter collectible attempts
   - `modifications` length is 1
   - `modifications[0].detail` exists
   - `modifications[0].diagnosis` exists
   - `modifications[0].intent` exists
   - `verdict` is one of `improved`, `stalled`, `regressed`, or it is the final unresolved attempt
4. Build observation records
   - Observation schema fields:
     - `id`
     - `record_kind`
     - `outcome`
     - `failure_type`
     - `error.message`
     - `environment.*`
     - `modification.*`
     - `result.*`
     - `source.*`
     - `superseded_by` for negative records
   - Store dedupe-only metadata under `_internal.*`
5. Link records within the same session
   - If a positive record follows a negative record for the same error in the same session, set `superseded_by` on the earlier negative record
6. Append to JSONL
   - Skip when the dedupe key `session_id + loop_kind + attempt + loop_epoch` already exists
   - For this check, reading `_internal.*` and `source.session_id` from existing `observations.jsonl` is allowed
   - Restrict the lookup to dedupe-only metadata comparison. Do not use it for semantic judgment
   - If append fails, emit only a warning and exit

## Collection Targets

- Single-change attempts from the Phase 4 analysis loop
- **Build-failure-based single-change attempts** from the Phase 5 test loop
- Both finally successful sessions and finally failed sessions

Call this wrap-up task only when the full-pipeline path completes. The caller is `ct-init-project` for end-to-end entry and `ct-orchestrator` for resume entry. Do not call it from the standalone `ct-test-loop` path.

## Exclusions

- Multi-change attempts
- Attempts missing `diagnosis`, `intent`, or `detail`
- Immediate success on the first attempt with no modification
- Test result `fail`
- Full rerun success after `reuse.fallback=true`
- Success after phase regression and regeneration

## Do and Don't

| Do | Do not |
|-----------|------------------|
| Extract only already recorded single-change attempts from `state.json` | Infer new root causes |
| Build observation records using the design-document schema | Rerun loops, modify conf, or roll back |
| Append to `observations.jsonl` | Read previous observations to make decisions |
| Exit with a warning only when it fails | Change session `status` |

## Observation Record Schema

```json
{
  "id": "OBS-20260402-001",
  "record_kind": "negative",
  "outcome": "no_effect",
  "failure_type": "analysis",
  "error": {
    "message": "identifier \"__packed\" is undefined"
  },
  "environment": {
    "compiler_type": "armcc",
    "compiler_version": "5.06",
    "target": "arm",
    "language": "C",
    "standard": "c99",
    "toolchain_kind": "armcc_50"
  },
  "modification": {
    "action": "conf_add",
    "detail": "cs_define_macro_name=__packed",
    "diagnosis": "__packed is an undefined compiler extension keyword in the host environment",
    "intent": "Define it as an empty macro so it is ignored"
  },
  "result": {
    "attempt_before": 1,
    "attempt_after": 2,
    "error_count_before": 15,
    "error_count_after": 15
  },
  "source": {
    "session_id": "20260402_demo",
    "created": "2026-04-02T15:00:00"
  },
  "superseded_by": "OBS-20260402-002",
  "_internal": {
    "loop_kind": "analysis",
    "attempt": 1,
    "loop_epoch": 1
  }
}
```

Notes:

- `id` follows the `OBS-{date}-{sequence}` rule.
- `record_kind`, `outcome`, and `failure_type` are determined from the phase and verdict.
- Store `_internal.loop_kind`, `_internal.attempt`, and `_internal.loop_epoch` so the dedupe key can be reconstructed from existing JSONL alone.
- `_internal.*` is storage-format-only metadata. Semantic interpretation belongs to the public schema fields.
- Set `superseded_by` only on negative records.

## Product-backed execution boundary

Canonical record mapping, deduplication, and linking rules are supplied with the installed CT/DVERA environment. Use them when available. If they are unavailable, summarize candidate observations without writing the product knowledge base, and direct the user to bizcenter@suresofttech.com.

## Notes

- `ct-kb-update` is not a regular phase. Do not assign it a phase number.
- Failure in this skill does not affect the session outcome.
- The current Phase 5 collection scope is limited to attempts with `failure_type="build"`.
- Use `test_execution` only when collection is later expanded to runtime execution failures.
- The source of truth for `loop_epoch` is the explicit state field. Read `analysis_loop.loop_epoch` and `test_loop.loop_epoch` directly.
- The actual runtime invocation path is `{ctPython} {ctTool} kb-update --session-id "{session_id}"`.
