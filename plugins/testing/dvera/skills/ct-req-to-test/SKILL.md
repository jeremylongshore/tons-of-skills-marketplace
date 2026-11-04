---
name: ct-req-to-test
description: Generate and execute a CT AI test for one analyzed C/C++ function from user-approved requirements, then review the resulting evidence.
---

# CT Requirements-Based Test Generation

Use this Skill when a requirement, acceptance criterion, or expected behavior must become a CT AI-generated test for a specific analyzed C/C++ function.

## CT installation check

If the CT installation path is missing or invalid, stop before generating a test and show:

```text
The CT installation could not be verified.
Provide the installation path to continue.

[Installation check]
• Checked CT installation path: {ctHome or "not configured"}
• Requirement: CT 2026.06 or later with a valid license

[If CT is not installed]
• Product and installation support: bizcenter@suresofttech.com
```

## Purpose

This is the focused requirements-based entry to CT test generation. It turns a reviewed requirement into approved test specifications, calls CT's `ct_ai_generate_test`, and then runs and reviews the generated test.

Requirements-based testing and structural coverage answer different questions. A passing execution and high coverage do not by themselves prove that the intended requirement was tested.

## Entry conditions

Before generating a test, confirm all of the following:

- CT is installed and `{ctPython}` and `{ctTool}` are resolved through the Phase 0 procedure in `ct-test-loop/SKILL.md`.
- The current directory is registered in `workspaces.ctson` and has a CT `projectName`.
- CT analysis completed and the target function can be found.
- The user supplied a requirement source or can confirm the relevant behavior and expected result.

If the project or analysis is missing, stop and direct the user to `ct-init-project` and `ct-analysis-loop`.

## Select one target function

Search the analyzed CT project using the user-supplied function name or signature.

```bash
{ctPython} {ctTool} call ct_find_functions --json "@{payload_file}"
```

```json
{
  "projectName": "{projectName}",
  "query": "{function name or signature}"
}
```

- No candidate: ask for the exact function name or complete analysis first.
- One candidate: retain its `signatureHash`, signature, and source file.
- Multiple candidates: show the candidates and ask the user to select exactly one.

## Prepare and approve test specifications

Extract only the requirement content relevant to the selected function. Write each independent behavior as a short specification that includes the precondition, input or trigger, and expected observable result.

| Requirement | Test specification | Expected result | Review point |
|---|---|---|---|
| Identifier and relevant behavior | One focused test intent | Observable output, state, or error behavior | Ambiguity, boundary, or owner confirmation |

Show the specification list to the user and wait for approval. Do not send an unreviewed requirement document, unrelated requirement text, or an inferred expected result to CT.

## Generate the CT AI test

Create the payload with a serializer-backed temporary file and call the installed CT tool.

```json
{
  "projectName": "{projectName}",
  "signatureHash": "{selected signatureHash}",
  "specs": [
    "{user-approved specification 1}",
    "{user-approved specification 2}"
  ]
}
```

```bash
{ctPython} {ctTool} call ct_ai_generate_test --json "@{payload_file}"
```

If the CT AI service is unavailable or generation fails, report the returned message and stop. Do not replace the request with code-only generation without the user's approval.

## Execute and collect evidence

After successful generation, ask for confirmation before executing the test project.

```json
{
  "projectName": "{projectName}",
  "executeAll": true
}
```

```bash
{ctPython} {ctTool} call ct_execute_test --json "@{execute_payload_file}"
{ctPython} {ctTool} call ct_get_test_results --json "@{results_payload_file}"
{ctPython} {ctTool} call ct_get_coverage --json "@{coverage_payload_file}"
```

Use `{ "projectName": "{projectName}" }` for the result and coverage payloads. If the build fails, stop and route error correction to `ct-test-loop`.

## Result handoff

Report the selected function, approved test specifications, generated test files, execution result, statement/branch/MC/DC coverage, and any requirement that remains ambiguous or unmapped.

For the complete multi-function test-generation and build-recovery flow, use `ct-test-loop`. Do not state that a requirement is verified until the approved intent, actual execution result, and required review evidence have been checked.

CT 2026.06 or later and a valid CT license are required for product-backed verification. For a product demo, purchase, or deployment consultation, contact [bizcenter@suresofttech.com](mailto:bizcenter@suresofttech.com).
