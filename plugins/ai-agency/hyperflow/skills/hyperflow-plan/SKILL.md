---
name: hyperflow-plan
description: Inspect a repository, resolve consequential decisions with the user, and save an approved Hyperflow workflow without executing it.
version: 8.0.0
---
# Hyperflow Plan

Use this skill for explicit planning and for requests whose scope or contract needs decisions before implementation. Planning is read only. Do not install dependencies, edit application files, launch providers, or execute a generated workflow.

## Start with the local runner

Resolve `<plugin-root>` to this installed plugin's directory. Invoke the runner with `node <plugin-root>/runtime/cli.mjs`. Never assume a `hyperflow` binary is on `PATH`.

1. Inspect the repository, Git state, relevant code, tests, existing `.hyperflow` data, conventions, and reusable components. This work is read only.
2. For a web-facing change, load `../hyperflow-smash/references/modern-web.md` before framing browser targets, progressive enhancements, or verification. Use it only when relevant.
3. Find the decision frontier: ask together only consequential questions whose prerequisites are settled. For each, include evidence, a recommendation, practical options, and whether it blocks work. Use the grill-me frontier method; do not copy upstream text.
4. Record the user's actual answers. Elapsed time, silence, a default, or a recommendation is not an answer.
5. Write a small planning draft JSON file in an allowed artifact directory, then let `plan <draft.json>` validate and persist it. The plan names scope, reuse, files and interfaces, task DAG, ownership, acceptance, checks, review, migration, and recovery where applicable.
6. Stop after compilation. A ready plan is not execution approval.

An explicit `/hyperflow-plan` always requests participation. If inspection finds no material ambiguity, present the concrete plan and ask for brief confirmation. Do not invent questions. Unanswered blocking questions prevent compilation.

## Workflow authority

The runner writes a static `workflow.mjs` declaration and a readable plan under `.hyperflow/workflows/<slug>/`. The declaration contains JSON-compatible data only. Do not place imports, executable expressions, arbitrary shell commands, or hidden side effects in it. The runner binds approval to a content digest; a material change requires a new reviewed plan. Task creation writes phase records: a workflow-wide planning file, per-task task, implementation, and correctness-review files, a consolidated security-review file, and a conditional security-fix file for every workflow. Compilation records the validated model and adapter and binds the phase-file digests into the approval receipt. These records carry the reviewed instructions; the compiled declaration remains execution authority.

At the user's explicit request, carry approved decisions forward as short, source-linked cards in `.hyperflow/memory/decisions.md`. Keep the task or spec authoritative, do not copy investigation transcripts, and do not load the ledger automatically at session start.

Each task carries actual nonblank details, a difficulty of `routine`, `complex`, or `security` (routine by default), and an explicit `low`, `medium`, or `high` effort. Routine tasks route to `lightweight`; complex and security tasks route to `general`; conflicting routing is rejected. Correctness review defaults to the `primary` role at high effort, and the workflow-wide security review and security fix lanes use the `general` role with high default effort. Show the resolved harness, provider/model, and effort. Never claim a model or effort is available until configuration and adapter validation succeeds. The active host remains the coordinator; a delegate profile never switches it. Use only capabilities exposed by the host running this chat.

Runtime methods:

```text
node <plugin-root>/runtime/cli.mjs plan <draft.json>
node <plugin-root>/runtime/cli.mjs answer <slug> <answers.json>
node <plugin-root>/runtime/cli.mjs compile <slug>
```

The answer document contains `{ "confirmed": true, "answers": { "Q1": "actual user answer" } }`. Obtain explicit confirmation when there are no blocking questions. The compiler writes a static workflow declaration and approval receipt; it does not execute either.

Use the local runtime's `--help` for exact argument forms. Do not hand-edit state to bypass validation.

## Writing

Before writing plans, questions, status updates, review findings or delivery summaries, apply the shared [unslop writing rules](references/unslop.md). Preserve technical meaning and evidence.

For React Native or Expo work, load the shared [mobile and Vercel React Native guidance](../hyperflow-crash/references/browser-mobile.md) before assigning tasks or accepting changes. Use the active harness for available device and profiling tools.
