---
name: ct-test-loop
description: Use this skill to generate and run tests on an analyzed CT project and correct build failures through a feedback loop. In standalone runs, you must first ask the user whether to use requirements-based or AI-code-analysis generation mode.
---

# /ct-test-loop - Test Generation and Execution (Phase 5)

**Primary request**: Use this skill when repeating test generation and execution while correcting build errors.

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

**Entry**: An analyzed CT project exists
**Input (standalone)**: `workspaces.ctson` entry keyed by CWD -> `projectName`
**Input (orchestrator-routed)**: in-memory state -> `ct_resources.project_name`
**Output (orchestrator-routed)**: in-memory state update (`status=test_success`, `test_results`, `coverage`)
**Execution mode**:
- **through `ct-orchestrator` (Phase 5)**: use in-memory state and run the default test generation flow
- **standalone (requirements-based)**: resolve `projectName` from `workspaces.ctson`, then generate tests from a requirements document plus coding context
- **standalone (AI code analysis)**: resolve `projectName` from `workspaces.ctson`, then let AI analyze the function source directly and generate tests without a requirements document

**Standalone guard**: At standalone entry, verify in two steps.
1. **Project registration**: If `workspaces.ctson` has no entry keyed by CWD -> **stop immediately** and tell the user "This directory is not registered as a CT project. Run `ct-init-project` first."
2. **Analysis completed**: Call `ct_get_functions(projectName)`. If the function list is empty -> **stop immediately** and tell the user "Analysis is not complete. Run `ct-analysis-loop` first."
**Precondition**: Use the variables acquired in "Phase 0 Initial Setup" (`ctHome`/`ctPython`/`ctTool`/`baseDir`, etc.). In end-to-end entry, `ct-init-project` prepares them. In resume entry, `ct-orchestrator` prepares them. In standalone entry, acquire them via the procedure below.

## Entry Mode Determination (Mandatory, Takes Precedence Over Other Procedures)

Before calling any test-generation tool (`ct_create_test`, `ct_ai_generate_test`), always run the two steps below.

1. **Decide the call path**: Determine the mode in the following order.
   - If the caller is `ct-orchestrator` and in-memory state was handed in -> **orchestrator-routed mode**.
   - If there is no in-memory state but the user's intent is to **resume an existing CT session** (e.g., "continue", "resume the interrupted work", "pick up from the saved state") -> this is an orchestrator intent, so do **not** treat it as standalone; **delegate to `ct-orchestrator`**, which reads `state.json` and resumes from the phase matching the current status. (Presence/absence of in-memory state alone cannot distinguish "resuming an existing session in a fresh session," so when resume intent is present, do not fall through to standalone.)
   - Otherwise (generating a test for a specific function, a fresh standalone request, etc.) -> **standalone mode**.
2. **Confirm the generation mode in standalone**: Right after passing the standalone guard (project registration + analysis completion above), you **must** show the standard prompt in the "Standalone Mode Selection" section and wait for the user's answer. Skip the prompt only when the user has already named a mode in their utterance (for example, "requirements-based", "by analyzing the code").

**Forbidden**:
- Do not call `ct_create_test` or `ct_ai_generate_test` before the mode (orchestrator-routed / standalone-requirements / standalone-AI-code-analysis) is confirmed.
- In standalone mode, do not apply the "Core sequence routed through `ct-orchestrator`" below. That sequence is for orchestrator-routed mode only.

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
  - Always distinguish **build failure** from **test result failure** by using `testRunSuccess`
  - Read logs only when the build fails, and record `build_succeeded`, `error_lines`, and `modifications` together in `test_loop.attempts[]`
  - Escalate system-header issues as a Phase 3 regression, and allow only `toolchain_kind` correction as an automatic Phase 5 repair
  - In standalone requirements-based mode, call test generation only after the function is fixed and the spec is approved
- **Do not**:
  - Read logs or attempt fixes when `testRunSuccess == true`
  - Assume that assertion failures, segfaults, or timeouts are environment issues
  - Overwrite existing link or compile flags
  - Try to solve system-header build errors directly in Phase 5
- **Why**:
  - In Phase 5, if you confuse "build failed" with "tests failed", you will misclassify real defects as environment issues
- **Stop and Ask summary**:
  - In standalone mode, if there are multiple candidate functions, do not choose without user confirmation.
  - Do not pass a standalone spec to `ct_ai_generate_test` without user approval.
  - If the same build-failure reason repeats, or the issue escalates to a runtime crash or timeout, stop and report to the user.
- **Safe pattern**:

```text
if testRunSuccess == true:
  collect results and stop
else:
  classify build/log errors -> apply only allowed auto-fixes -> retry
```

## Pre-Work Gate Check

1. Confirm that `project_name` and `working_directory` exist and that the current phase is really Phase 5
2. Decide first whether the current loop is handling a build failure or just reporting normal execution results
3. Confirm that no user-confirmation step remains unresolved, such as function selection or requirements-spec approval
4. If this is a build failure, decide the log classes and maximum read range before starting

**Standalone entry procedure**:
1. **Initial environment setup** — Apply the "Phase 0 Initial Setup" procedure from `ct-init-project/SKILL.md` to acquire `ctHome` / `ctPython` / `ctTool` / `baseDir`. (Skip the workspace-selection step in standalone — step 2 below replaces it.)
2. **Resolve `projectName`**
   a. Use the Read tool to read `{baseDir}/workspaces.ctson`.
   b. Parse the JSON. Schema: `{ "{sourceDir}": { "workspaces": [ { "path": "...", "projects": [...] } ] } }`
   c. Look up the entry keyed by the **current CWD** as `sourceDir`. Be careful with OS-specific path normalization (drive-letter case, slash direction).
   d. Determine `projectName` from `workspaces[0].projects` (per the schema, `workspaces[0]` is the active one).
      - One project -> auto-select
      - Multiple projects -> show the list and ask the user to choose
   e. **Standalone guard (1)** — if the entry is missing or `projects` is empty, stop with "This directory is not registered as a CT project. Run `ct-init-project` first."
3. **Verify analysis completion** — Call `ct_get_functions(projectName)`. If the function list is empty, treat it as **standalone guard (2)** and stop with "Analysis is not complete. Run `ct-analysis-loop` first."

**Phase 0 variables** (acquired by `ct-init-project` in end-to-end entry, `ct-orchestrator` in resume entry, or step 1 above in standalone entry):
- `{ctPython}`: Python executable path based on `ct_get_env.pythonPath`
- `{ctTool}`: `ct_tool.py` execution path
- `skillResourceRoot`: autoconfig path from `ct_get_env.skillResourceRoot`
- `metaDir`: metadata path from `ct_get_env.metaDir`

**CT functions** (used in Phase 5):
- `ct_get_functions(projectName)` - function list
- `ct_find_functions(projectName, query)` - similarity-based candidate search for standalone requirements-based mode
- `ct_create_test(projectName, target)` - generate tests
- `ct_ai_generate_test(projectName, signatureHash, specs?)` - AI test generation. `specs` is an array of requirement strings. With `specs`, use requirements-based generation; without it, use CT built-in AI code analysis
- `ct_execute_test(projectName, executeAll)` - execute tests
- `ct_get_test_results(projectName)` - retrieve results
- `ct_get_coverage(projectName)` - retrieve coverage
- `ct_generate_report(projectName, outputDir, formats?)` - generate reports (optional). `formats` accepts one or more of `pdf`, `html`, `xlsx`, `xls`, `docx`, `doc`, `pptx`, `ppt` (defaults to `["pdf"]`)
- `ct_set_link_flags(projectName, linkFlags)` - modify link flags
- `ct_set_compile_flags(projectName, compileFlags)` - modify compile flags
- `ct_modify_toolchain(toolchainId, iniFilePath?)` - apply ini changes when correcting `toolchain_kind`. **After this call, do not call `ct_set_project_toolchain`**. An ini-only call does not require `confType` or `language`, and those parameters do not affect it.

**ct_create_test target rule**: use the official target `untested_functions` for untested functions. Common aliases such as `untested` and `untested_function` are accepted when no function name matches.

**`ct-orchestrator`-routed test mode core sequence** (default test generation; apply only when "Entry Mode Determination" confirmed orchestrator-routed mode):
1. Run `ct_get_functions` -> stop if the function count is 0
2. Select **exactly one** function from the function list -> `ct_create_test(target="{function_name}")`
   - This is the minimal test used to validate the environment while conserving resources
   - Selection order: function defined in user source first -> fewer parameters -> function name lexicographic order -> signatureHash lexicographic order
3. Feedback loop (up to 5 attempts):
   a. `ct_execute_test(executeAll=true)`
   b. **If `testRunSuccess == true`** -> the build succeeded -> run `ct_get_test_results` + `ct_get_coverage` -> **stop immediately**. Even if individual tests are `error` or `fail`, do not analyze logs
   c. **If `testRunSuccess == false`** -> the build failed **or a pilot/runtime failure** -> classify errors from logs:
      - Compile error: `log/build/{ModuleName}/*.log.txt`
      - Link error: `log/build/link.log.txt`
      - Full flow: `log/engine.log`
      Classification actions:
      - `undefined reference` -> add `-l` to `ct_set_link_flags`
      - Project header missing -> add `-I` to `ct_set_compile_flags`
      - **System header missing -> regress to Phase 3** (do not resolve it in Phase 5)
      - **C++11+ keyword errors such as `constexpr`, `nullptr`, or `char16_t` in system headers** -> `toolchain_kind` mismatch. Correct `toolchain_kind` in the ini to the matching host GCC version (Linux requires the `_64` suffix, for example `95_64`), then run `ct_modify_toolchain(toolchainId, iniFilePath)` -> rerun `ct_analyze` -> rerun `ct_execute_test`. Do not call `ct_set_project_toolchain`
      - **Build succeeded (`testrun.exe` exists and `link.log` is empty) but runtime execution does not start** -> treat it as a runtime failure, not a build failure. Do not apply link/include flag fixes. Use canonical diagnostic guidance from the installed CT/DVERA environment; if unavailable or the failure persists, stop and report the evidence to the user.

---

## Standalone Mode Selection

In standalone execution, immediately after passing the standalone guard (project registration + analysis completion), ask the user how tests should be generated.

```text
How would you like to generate the tests?

  1. Requirements-based test generation
     - Generate spec-driven tests using requirements documents plus coding context
     - Preserves design intent, boundary values, and exception handling in the test spec

  2. AI code analysis-based test generation
     - AI analyzes the function source directly without requirements documents
     - Useful for legacy code or when no requirements document exists
```

-> If the user selects 1: proceed to "Standalone execution procedure (requirements-based)"
-> If the user selects 2: proceed to "Standalone execution procedure (AI code analysis-based)"

---

## Standalone Execution Procedure (Requirements-Based Test Generation)

Follow the procedure below only in standalone mode. Do not run this inside the `ct-orchestrator`-routed test mode.

### Step 1: Confirm the Project

Use the `projectName` identified in step 2 of the standalone entry procedure above.

### Step 2: Search Functions

Call `ct_find_functions` with the function name or signature mentioned by the user as the query.

**Branch on result**:
- `totalCount == 0`: function not found -> ask the user for the exact function name again
- `totalCount == 1`: confirm automatically without asking the user
- `totalCount >= 2`: show the candidate list and ask the user to choose

Remember the selected function's `signatureHash`, `signature`, and `sourceFile`.

### Step 3: Collect Requirements Documents

**Priority**:
1. If a requirements document is already referenced in the current conversation context, use that file first
2. Otherwise scan recursively under the current working directory:
   - Directories: `requirements/`, `req/`, `specs/`, `spec/`, `docs/`, `doc/`, and the repository root `.`
   - Files: `*.md`, `*.txt`, `*.rst`, `*.pdf`, `*.docx`, `*.xlsx`, `*.html`, `*.htm`
   - Prefer filenames containing `requirement`, `req`, `spec`, `srs`, or `irs`
   - Read text formats (`md`, `txt`, `rst`, `html`) directly. For binary formats (`pdf`, `docx`, `xlsx`), read them only if the tool supports it. Otherwise show the file path and ask the user to provide the relevant content

**Branch on file count**:
- `0`: ask the user for the requirements document path
- `1~5`: use them as-is
- `6+`: show the list and ask the user to choose

### Step 4: Write the Specification

Build the specs by combining the two sources below. Split distinct requirements into separate strings when possible.

**A. Coding context** - content from the current conversation that must be reflected in tests:
- Bugs, workaround code, or exception handling discovered during implementation
- Input ranges discussed as boundary or edge cases
- Design decisions such as "return an error code for negative input"

**B. Requirements documents** - extract only content related to the target function from the collected documents:
- Functional requirements, preconditions, postconditions, input-output constraints
- Exclude unrelated requirements for other features

After writing the specs, **show the list to the user and ask for confirmation or edits**.
If the user provides feedback, apply it, show the specs again, and reconfirm.
Proceed only after the user approves the specs.

### Step 5: Generate the Test

Call `ct_ai_generate_test` with the approved specs list and `signatureHash`.

```text
ct_ai_generate_test {
  "projectName": "{identified projectName}",
  "signatureHash": "{signatureHash of the confirmed function}",
  "specs": [
    "{user-approved spec 1}",
    "{user-approved spec 2}"
  ]
}
```

### Step 6: Report the Result

- `targetFunctionCount`: number of target functions processed (1 in this flow)
- `generatedTestCount`: total number of generated test files
- `generatedTestFiles`: list of generated test file names
- `message`: server message

---

## Standalone Execution Procedure (AI Code Analysis-Based Test Generation)

In this mode, AI analyzes the function source directly and generates tests without a requirements document. Do not run this inside the `ct-orchestrator`-routed test mode.

### Step 1: Confirm the Project

Use the `projectName` identified in step 2 of the standalone entry procedure above.

### Step 2: Search Functions

Call `ct_find_functions` with the function name or signature mentioned by the user as the query.

**Branch on result**:
- `totalCount == 0`: function not found -> ask the user for the exact function name again
- `totalCount == 1`: confirm automatically without asking the user
- `totalCount >= 2`: show the candidate list and ask the user to choose

Remember the selected function's `signatureHash`.

### Step 3: Generate the AI Test

Call the CT built-in AI test generation function (`ct_ai_generate_test`). AI analyzes function source code and type information, generates code-based tests, and automatically corrects compile errors through its internal feedback loop.

```text
ct_ai_generate_test {
  "projectName": "{identified projectName}",
  "signatureHash": "{signatureHash of the confirmed function}"
}
```

**Precondition**: the CT AI server must already be configured. If not, report the error to the user and stop.

### Step 4: Report the Result

- `targetFunctionCount`: number of target functions processed (1 in this flow)
- `generatedTestCount`: total number of generated test files
- `generatedTestFiles`: list of generated test file names
- `message`: server message

**Forbidden in AI code analysis mode**:
- Do not ask for user confirmation when `totalCount == 1`. Confirm automatically
- Do not write specs or ask the user to confirm specs. This mode runs without them

**Standalone forbidden rules**:
- Do not ask for user confirmation when `totalCount == 1`. Confirm automatically
- Do not call `ct_ai_generate_test` without user confirmation for the specs in the requirements-based mode
- Do not include the entire requirements document verbatim in the specs. Extract and summarize only the parts related to the target function
- If coding context does not exist, state that explicitly and write the specs from the requirements document alone

---

**Single-change recording rules**:
- Observation collection in Phase 5 currently targets **build-failure attempts first**
- Keep `modifications` as an array for each attempt
- **Only when there is exactly one modification**, record `detail`, `diagnosis`, and `intent` inside `modifications[0]`
- `detail` is the required string for observation-record collection
- If there are 2 or more modifications, do not record `diagnosis` or `intent`
- Normal test execution results with `testRunSuccess == true` are not observation-record targets

**Important: build errors vs test result errors must be distinguished**
- `testRunSuccess == true` -> the build succeeded. Even if individual tests are `error` or `fail`, this is a **test execution result**. Do **not** analyze logs. Report the result and finish
- `testRunSuccess == false` -> the build failed. Only in this case should you analyze logs and try fixes

**Note**: `ct_set_compile_flags` applies **only to analysis preprocessing** and is not passed to the test build command. Macros or types needed for the build must be resolved at the conf level or included in the preprocessing result.

**Forbidden**:
- When `testRunSuccess == true`, do not read logs, analyze them, or attempt fixes. Report the result and finish
- Do not try to solve system-header build errors in Phase 5. Regress to Phase 3 instead
- Do not overwrite existing link or compile flags. Add cumulatively
- Do not try to fix build errors with `ct_set_compile_flags`. Those flags are not passed to the build, so resolve it through conf changes instead

## Output Schema (fields added or updated on Phase 5 success)

```json
{
  "status": "test_success",
  "test_loop": {
    "attempt_count": 2,
    "max_attempts": 5,
    "loop_epoch": 1,
    "target_functions": ["Board_init"],
    "attempts": [
      {
        "attempt": 1,
        "result": "failed",
        "verdict": "stalled",
        "build_succeeded": false,
        "error_lines": ["undefined reference to `Board_init`"],
        "modifications": [
          {
            "action": "link_flag_add",
            "detail": "-lboard",
            "diagnosis": "The board library symbol is missing during the test link step",
            "intent": "Add the missing library link flag"
          }
        ]
      },
      {
        "attempt": 2,
        "result": "success",
        "verdict": "improved",
        "build_succeeded": true,
        "error_lines": [],
        "modifications": []
      }
    ]
  },
  "test_results": {
    "testRunSuccess": true,
    "total": 1,
    "passed": 1,
    "failed": 0,
    "tests": [{ "testName": "Board_init_TC1", "suiteName": "GeneratedSuite", "status": "Success" }]
  },
  "coverage": { "statement": "100%", "branch": "100%", "mcdc": "N/A" }
}
```

**Minimum validator contract**:
- If `test_loop` exists, it must contain `attempt_count`, `loop_epoch`, and `attempts[]`
- If `verdict` is recorded, the only allowed values are `improved`, `stalled`, and `regressed`
- If `modifications` length is 1, `modifications[0]` must be an object, and `detail`, `diagnosis`, and `intent` must be non-empty strings
**Documentation conventions**:
- Keep `coverage` at the top level, not under `test_results`
- The current validator requires top-level `coverage` only when `status=test_success` and `test_results.testRunSuccess=true`
- Keep `test_results.tests` as an example array of `{ testName, suiteName, status }` objects
- For multi-change attempts, keep only the `modifications` array and omit `diagnosis` and `intent`

## Product-backed execution boundary

Detailed error classification, loop control, and final state validation are supplied with the installed CT/DVERA environment. Use its canonical documentation when available. If it is unavailable, do not execute or modify CT test assets; summarize the prepared test intent and direct the user to bizcenter@suresofttech.com.
