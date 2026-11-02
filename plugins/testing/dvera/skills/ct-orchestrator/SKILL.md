---
name: ct-orchestrator
description: Use this skill to continue an existing `state.json` session and decide whether to resume `ct-init-project`, `ct-analysis-loop`, or `ct-test-loop` from the current status.
---

# /ct-orchestrator - Continue Progress

**Primary request**: Use this skill when continuing an interrupted CT flow from the next stage.

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

## Summary

**Role**: In a resume session, confirm the execution environment, read `state.json`, determine the current phase range from `status`, choose the representative skill among `ct-init-project`, `ct-analysis-loop`, and `ct-test-loop`, run **state.json validation (step 4.5)**, and then ask the user before crossing the next representative stage boundary.

**status <-> phase mapping**: `pending` enters Phase 1 by default. However, if `toolchain_mode=host` is already confirmed and `toolchain_mode_user_confirmed=true`, it enters Phase 3 directly. `macros_extracted` means Phase 2, `conf_generated` means Phase 3, `project_created` means Phase 4, `analysis_success` means Phase 5, and `test_success` means the whole pipeline is complete. `*_ing` states rerun the same phase. `*_failed_*` states are failure-reporting states.

**User stage labels**: explain Phases 1, 2, and 3 as `Project preparation`, Phase 4 as `Analysis`, and Phase 5 as `Test`. In user-facing progress, completion, and failure messages, use those three stage labels instead of phase numbers.

**Broad entry boundary**: new CT-apply requests and full CT-apply requests are handled by `ct-init-project`. `ct-orchestrator` handles only resume, continue, and state-based entry.

**Fingerprint validation**: On session resume, fingerprint validation runs only in `conversion` mode. If the conf or ini hash is different, ask the user whether they edited it directly. If the answer is `y`, recalculate the fingerprint. If the answer is `n`, roll back to the phase that produced that artifact.

**Document loading**: When entering a phase, read that phase skill's `SKILL.md`. Use canonical product documentation from the installed CT/DVERA environment only when product-specific execution or recovery is required. Always record loaded documents in the format `Loaded docs: [...]`.

**Phase transition**: Do not automatically advance to the next phase after one phase completes. Always ask the user.

**Regression**: Do not regress for the same reason more than twice. Escalate to the user if it repeats.

---

This skill resumes an interrupted CT application flow.
It reads `state.json`, determines the current phase range, and routes to the representative skill flow that should continue next.
Even if the session was interrupted, calling `/ct-orchestrator` again resumes the flow.

## Pipeline Overview

```text
[Conversion toolchain]
Phase 1: extract-macro     Shared environment analysis + mode confirmation + macro extraction
Phase 2: make-conf         Generate conf/ini
Phase 3: setup-project     Create toolchain + CT project
Phase 4: analysis-loop     PA analysis + error feedback loop
Phase 5: test-loop         Test generation/execution + build feedback loop
Post-hook: ct-kb-update    Collect observation records (best-effort, not a regular phase)

[Host toolchain]
Phase 1: extract-macro     Shared environment analysis + host toolchain candidate decision/confirmation
Phase 3: setup-project     Select an existing host toolchain + create CT project
Phase 4: analysis-loop     PA analysis + error feedback loop
Phase 5: test-loop         Test generation/execution + build feedback loop
Post-hook: ct-kb-update    Collect observation records (best-effort, not a regular phase)
```

## Global Rules

### Document Loading Rules

- When entering a phase, read only that skill's `SKILL.md`, for example `ct-{skill}/SKILL.md`
- At phase start, always print `Loaded docs: [ct-{skill}/SKILL.md]`
- When product-specific execution or recovery is required, use canonical documentation supplied by the installed CT/DVERA environment and include it in `Loaded docs`
- If that documentation or the installed integration is unavailable, keep the work at preparation and planning level; do not guess CT operations

### Product Guidance

- Load diagnostic guidance only after the first failure or when a phase skill explicitly requires it
- Treat installed product guidance as canonical when it differs from this public workflow

### state.json Rules

- Do not read the same file again immediately after a `Write`
- Treat the in-memory state as the canonical source
- The rule is `read-once at phase entry`, `write-once at phase exit`, and `re-read only after external mutation`
- Re-read `state.json` only when resuming a session

### File and Encoding Rules

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

### Path and Naming Rules

- Record only absolute paths in `state.json`. If a relative path appears, convert it to an absolute path immediately
- Toolchain name: `{session_id}_{HHmmss}_tc`
- Project name: `{session_id}_{HHmmss}_project`

### Execution Guardrails

- **Do**:
  - Before phase transition, validate `toolchain_mode`, fingerprint resolution state, and user confirmation state first
  - Patch only the fields used by the current phase, and do not pre-create fields for the next phase
- Pass CT function payloads with a serializer or with safe patterns such as `--json '@-'` or `--json @file`
- **Do not**:
  - Confirm `toolchain_mode` without Phase 1 evidence and user confirmation
  - Overwrite a `conversion` fingerprint mismatch by guesswork
  - Automatically proceed to the next phase without user confirmation
  - Build new one-line payloads where path, JSON, and Python code are nested in one string
- **Why**:
  - A wrong decision in `ct-orchestrator` breaks the input contract for every later phase and creates the highest regression cost
- **Stop and Ask summary**:
  - If `toolchain_mode` is unresolved or `toolchain_mode_user_confirmed` is missing, stop and confirm.
  - In `conversion`, if the conf or ini fingerprint mismatch is not resolved, stop and confirm.
  - Never skip user-intent steps such as source scope selection or host toolchain selection.
- **Safe pattern**:

```powershell
$jsonArgs = @'
{"toolchainName":"demo_tc","confFilePath":"C:/ws/demo.conf"}
'@

$jsonArgs | & {ctPython} {ctTool} 'call' 'ct_create_toolchain' '--json' '@-'
```

### Pre-Work Gate Check

1. Confirm that the session's `toolchain_mode` and user confirmation state match the phase transition rule
2. In `conversion`, confirm that a fingerprint mismatch has already been resolved by user confirmation or recalculation
3. Confirm that the state patch you are about to write contains **only current-phase fields**
4. Confirm again whether the next phase requires user confirmation before transition

### Phase 0 Bootstrap Rules

- The canonical source of the Phase 0 initial setup procedure is `ct-init-project`.
- If the resume session's `bootstrap` data is missing or fails validation, follow the `## Phase 0 Initial Setup Rules` and `## Step 0: Phase 0 Initial Setup` procedures in `ct-init-project/SKILL.md` exactly.
- Do not redefine the Phase 0 details in this skill.
- If both the resume session's `bootstrap` data and Phase 0 output paths are valid, do not rerun Phase 0; continue with the next-stage decision.

## Execution Procedure

### Step 0: Phase 0 Bootstrap

Determine whether Phase 0 is needed only for resume sessions.

1. First, validate the `bootstrap` data and Phase 0 output paths in `state.json`.
2. If they are valid, do not rerun Phase 0; continue with the next-stage decision.
3. If they are missing or fail validation, follow the `## Phase 0 Initial Setup Rules` and `## Step 0: Phase 0 Initial Setup` procedures in `ct-init-project/SKILL.md` to restore Phase 0.
4. Do not decide `toolchain_mode` in Phase 0. Decide it from the Phase 1 shared-environment analysis and user confirmation.
5. Only if Phase 0 was actually restored, summarize the current values in the same Session bootstrap card format for later reference. Do not reprint the card when all existing bootstrap values are valid and Phase 0 was skipped.

### Step 1: Initialize the Session

If there is no session ID, create one.

- Rule: `{YYYYMMDD}_{project_directory_name}`
- Example: `20260311_ccsblink`
- Working directory: `{sessionsBase}/{session_id}/`
- Record the bootstrap fields below into `state.json`

```json
{
  "bootstrap": {
    "ct_home": "{ctHome}",
    "ct_python": "{ctPython}",
    "ct_tool": "{ctTool}",
    "skill_resource_root": "{skillResourceRoot}",
    "tool_root": "{toolRoot}",
    "meta_dir": "{metaDir}",
    "sessions_base": "{sessionsBase}"
  }
}
```

### Step 2: Load state.json and Decide the Current Phase Range

Read `{sessionsBase}/{session_id}/state.json`.

**If the file does not exist**: report that there is no resumable session state yet and tell the user to start with `ct-init-project`.

**If the file exists**: decide the entry phase from `status`.

| status | Meaning | Entry phase |
|--------|------|-----------|
| `pending` or missing | before start | Phase 1 by default. However, enter Phase 3 if `toolchain_mode=host` and `toolchain_mode_user_confirmed=true` |
| `extracting_macros` | interrupted during Phase 1 | rerun Phase 1 |
| `macros_extracted` | Phase 1 complete | Phase 2 |
| `generating_conf` | interrupted during Phase 2 | rerun Phase 2 |
| `conf_generated` | Phase 2 complete | Phase 3 |
| `setting_up_project` | interrupted during Phase 3 | rerun Phase 3 |
| `project_created` | Phase 3 complete | Phase 4 |
| `analyzing` | interrupted during Phase 4 | rerun Phase 4 |
| `analysis_success` | Phase 4 complete | Phase 5 |
| `testing` | interrupted during Phase 5 | rerun Phase 5 |
| `test_success` | full completion | report completion |
| `regression_done` | regression check finished on a completed pipeline | report the `regression` object, then treat the pipeline as complete. Re-enter Phase 5 only if the user wants to act on `new_failures` |
| `*_failed_*` | failure state | report failure and ask about retry |
| anything else | status written by a skill this table does not cover | do not guess a phase. Show the status and the `artifacts` present, and ask the user which phase to resume from |

### Step 3: Fingerprint Validation on Resume

When resuming from Phase 2 or later, confirm artifact validity. Fingerprint validation applies only to `conversion` mode.

**Standard prompt**:

```text
The analysis configuration file (conf) has changed since it was last recorded. Did you modify it directly? (y/n)
```

```text
The toolchain metadata file (ini) has changed since it was last recorded. Did you modify it directly? (y/n)
```

**Sequential validation rules**:

| Current status | Validation target | If mismatched |
|-------------|----------|----------|
| `conversion` + `conf_generated` or later | `fingerprints.conf_hash` vs actual conf file hash | Ask the user. If `y`, recalculate `conf_hash`. If `n`, rerun from Phase 2 |
| `conversion` + `project_created` or later | `fingerprints.ini_hash` vs actual ini file hash | Ask the user. If `y`, recalculate `ini_hash`. If `n`, rerun from Phase 3 |

Additional rules:
- `host` mode does not enforce conf or ini fingerprints
- In `conversion`, the conf fingerprint source must satisfy both the top-level `conf_path` canonical field and the `artifacts.conf_path` mirror contract. If either is missing or they point to different paths, treat it as a Phase 2 regression target without asking
- In `conversion`, use `artifacts.meta_ini_path` as the ini fingerprint source
- In `conf_generated`, validate only `conf_hash` and do not check `ini_hash`
- In `project_created` or later, check `conf_hash` first and check `ini_hash` only if `conf_hash` passes
- If Phase 4 intentionally modified the conversion conf, update `fingerprints.conf_hash` immediately inside the same phase
- If `toolchain_mode` is missing in a legacy `state.json`, confirm the mode with the user before fingerprint validation

### Step 4: Execute the Phase

Read the representative skill document for the current phase range and follow that logic. For the Phase 1/2/3 range, the orchestrator must route through `ct-init-project` instead of reading the internal phase skills directly.

| Phase range | Status range | Representative skill | Routed mode | SKILL.md |
|-----------|-------------|-----------|-----------|----------|
| Phase 1/2/3 (Project preparation) | `pending`, `extracting_macros`, `macros_extracted`, `generating_conf`, `conf_generated`, `setting_up_project` | `ct-init-project` | `ct-orchestrator`-routed project-preparation mode (internally follows the project-preparation-only procedure) | `ct-init-project/SKILL.md` |
| Phase 4 (Analysis) | `project_created`, `analyzing` | `ct-analysis-loop` | `ct-orchestrator`-routed analysis mode | `ct-analysis-loop/SKILL.md` |
| Phase 5 (Test) | `analysis_success`, `testing` | `ct-test-loop` | `ct-orchestrator`-routed test mode | `ct-test-loop/SKILL.md` |

Rules:

- On Phase 1/2/3 resume, the orchestrator reads `ct-init-project/SKILL.md` and follows that skill. `ct-init-project` internally reads `ct-extract-macro/SKILL.md`, `ct-make-conf/SKILL.md`, and `ct-setup-project/SKILL.md` as needed. The orchestrator does not read those internal phase skills directly.
- On Phase 1/2/3 resume, user-facing messages must bundle the flow as `Project preparation`.
- `ct-init-project` project-preparation mode resumes from the required internal phase (1/2/3) based on the current `status`. The orchestrator passes the state and delegates internal phase selection to `ct-init-project`.
- For Phase 4 and Phase 5, read the representative skill directly. Do not introduce extra routed skills.
- Use installed product guidance only when the representative skill requires product-specific execution or recovery.

### Step 4.5: Validate state.json

After each phase completes and before moving to the next phase, validate the state.

```bash
{ctPython} {skillResourceRoot}/engine/validate_state.py "{session_dir}" {phase_number}
```

- Validate the host pre-Phase3 state (`status=pending`, `toolchain_mode=host`, `toolchain_mode_user_confirmed=true`) with `phase_number=1`
- Use `phase_number=3` only after `host_toolchain` and `ct_resources.*` exist in the completed host project-created state
- `OK`: valid, move to the next phase
- `CORRECTED: ...`: auto-correction completed. Review the correction and continue
- Error (exit 1): use the stderr message, fix only the current phase's `state.json` output, and validate again

After validation, do not re-read state. Assume corrections are already reflected in the in-memory state.

### Step 4.6: Post-Hook

After Phase 5, call `ct-kb-update` once as a **wrap-up task, not as a regular phase**.

```bash
{ctPython} {ctTool} kb-update --session-id "{session_id}"
```

Rules:
- `kb-update` is a subcommand of `ct_tool.py`
- This path is best-effort and separate from Bridge state
- Call it once immediately after reaching `test_success`
- Do not call it for the standalone `ct-test-loop` path
- Even if `ct-kb-update` fails, do not change `status`
- Leave `observations.jsonl` append failure as a warning only
- Prevent duplicate records based on `session_id + loop_kind + attempt + loop_epoch`

Input:
- Final in-memory state or the latest `state.json`
- `session_id`
- `bootstrap.sessions_base`
- `analysis_loop.attempts[]`, `test_loop.attempts[]`
- `analysis_loop.loop_epoch`, `test_loop.loop_epoch`

### Step 5: Representative Stage Transition

In this section, `{stage label}` means only the representative user stage (`Project preparation`, `Analysis`, `Test`). It does not mean the internal phase number. Phases 1, 2, and 3 belong to `Project preparation`, Phase 4 belongs to `Analysis`, and Phase 5 belongs to `Test`.

**Auto-advance ranges** - continue without asking the user:
- Phase 1 -> Phase 2 (inside project preparation)
- Phase 2 -> Phase 3 (inside project preparation)
- Internal retries inside Phase 4 and Phase 5

**User-confirmation ranges** - ask only at representative stage boundaries:
- Phase 3 -> Phase 4 (Preparation -> Analysis)
- Phase 4 -> Phase 5 (Analysis -> Test)

When confirmation is required at a representative stage boundary, use the format below.

```text
{Current stage label} is complete. Proceed to {Next stage label} next?
(If the context is too heavy, you can run /clear and continue again with /ct-orchestrator.)
```

- Put one of `Project preparation`, `Analysis`, or `Test` into the labels above. Do not print the phase number.
- Proceed only if the user confirms.
- If the user defers, stop at the current state.
- Even when a resume session enters in the middle of Phases 1, 2, and 3, user-facing messages must still bundle it as `Project preparation`.

## Regression Handling

When regression is required in Phase 4 or 5:

1. Decide whether regression is needed from the current skill instructions
2. Record a `regression` object in `state.json`
3. Change `status` to the entry state of the regression target phase
4. Run that phase's skill logic again
5. Return to the original flow after the regression phase completes

**Regression summary**

| Error type | Where it happens | Regression target |
|-----------|----------|----------|
| setting application failure | Phase 4 | Phase 3 |
| fundamental conf issue | Phase 4 | Phase 2 |
| polluted macro dump | Phase 4 | Phase 1 |
| system header build error | Phase 5 | Phase 3 |
| memory structure or uninterpretable issue | Phase 4/5 | escalate to the user |
| assertion failure | Phase 5 | escalate to the user |

Do not regress more than twice for the same reason.

## Failure State Handling

If `status` is `*_failed_*`:

1. Show the failure history to the user
2. Present the options below
- Retry the same phase
- Rerun from a previous phase
- Stop
3. Adjust `status` and required counters according to the user's choice and continue

Use the label below in user-facing failure reports.

```text
{Project preparation | Analysis | Test} stopped.
```

## Completion Report

If Phase 5 succeeds, report in the format below.

```text
CT pipeline completed:
- Session: {session_id}
- Project preparation: complete
- Analysis: success ({N} functions)
- Test: ran {totalTests} tests, {passed} passed, {failed} failed
- Coverage: Statement {X}%, Branch {Y}%, MC/DC {Z}%
- Attempt counts: analysis {M}, test {K}
```

## Notes

- `ct-orchestrator` decides the state and representative-skill transitions. Detailed per-phase logic belongs to each skill's `SKILL.md`
- Always ask the user before phase transition. Never proceed automatically
- If resuming from a `*_ing` state, rerun that phase from the beginning
- If the context gets heavy, recommend `/clear` and then call `/ct-orchestrator` again. The state remains in `state.json`
- Even when the user wants to run only a single phase, do not skip the current required phase. Missing prerequisite outputs and `status/artifacts` cause larger failures later
- Do not re-read `state.json` immediately after writing it
- Do not call CT functions directly. In later phases as well, always use the form `ct_tool.py call <tool>`
- At phase start, record the loaded documents as `Loaded docs: [...]` so the reference set is explicit
