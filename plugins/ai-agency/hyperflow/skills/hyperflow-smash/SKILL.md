---
name: hyperflow-smash
description: Execute a selected, reviewed Hyperflow workflow through isolated tasks, independent review, scoped repair, and real verification.
version: 8.0.0
---
# Hyperflow Smash

Use only when the user explicitly starts an approved workflow with `/hyperflow-smash` or an equivalent direct request. This invocation authorizes execution of that workflow version. A plan alone does not. For web-facing work, load `references/modern-web.md` and include applicable browser targets, progressive fallbacks, and evidence in the task plan.

## Unattended execution

Starting smash authorizes full-access, noninteractive implementation of the selected workflow. Use the selected delegate harness's supported permission controls. Do not ask questions, request routine confirmation, or pause between tasks, checks, reviews, or fixes. Resolve implementation details from the approved plan and repository. Keep progress updates brief and continue until every runnable task has finished.

The runtime passes full-access options to writing delegates. OpenCode and Pi use their noninteractive writing defaults. Fresh reviewers remain read only. These settings apply to delegated processes; the coordinator uses the permissions provided by its host. Do not invent an override for host-enforced restrictions.

If required access, credentials, tools, or a consequential decision outside the approved plan is unavailable, record a concrete blocker without waiting for input. Continue independent tasks and report unresolved blockers at the end. Preserve task ownership, user files, verification, and stop controls.

## Run

Resolve `<plugin-root>` to this installed plugin's directory. Invoke `node <plugin-root>/runtime/cli.mjs`; do not assume a global binary.

```text
node <plugin-root>/runtime/cli.mjs smash <workflow.mjs>
```

Before dispatch, validate workflow digest, unanswered blocking questions, repository identity, role revision, model bindings, ownership, checks, and available tools. Execution requires a schema-2 approval receipt; its digests cover the compiled declaration, the model role bindings, and every generated phase record. Missing, edited, or symlinked phase files block dispatch, and schema-1 plans refuse with replanning guidance. Changed authority requires replanning. Use isolated task worktrees, bounded source-linked context including the task details, durable claims, and the configured provider adapter. Preserve dirty user work and shared files.

Schedule by dependency and write-scope readiness, not by task numbering. Independent ready work can overlap within measured host/provider capacity. Review each candidate in a fresh independent primary correctness session — a new lane with its own context and an isolated checkout, never a reused session — before serial integration. The worker cannot review or approve its own work. Route validated findings to the responsible worker, rerun affected checks, and re-review changed risk areas. Cap automatic correction at two rounds for an unchanged contract and failure signature.

After all implementation and correctness phases finish, one consolidated security review by the `general` role runs once on the integrated candidate, before changes reach the user checkout. Its validated findings are implemented in a new independent `general` fix lane; fixes rerun the affected checks, the primary correctness review, and security revalidation. A failure or blocked verdict, a contradiction, a stop, or a candidate mutation prevents applying the workflow; never reuse a stale verdict.

Do not manufacture completion from a model summary, exit code, empty diff, or reviewer verdict. Report integrated evidence, blocked/unavailable checks, and remaining limits accurately. Installation and planning never execute a workflow.

## Operations

Operational controls stay under smash:

```text
node <plugin-root>/runtime/cli.mjs status <run-id>
node <plugin-root>/runtime/cli.mjs graph <run-id>
node <plugin-root>/runtime/cli.mjs stop <run-id>
node <plugin-root>/runtime/cli.mjs resume <run-id>
node <plugin-root>/runtime/cli.mjs sessions
node <plugin-root>/runtime/cli.mjs rename <run-id> <label>
node <plugin-root>/runtime/cli.mjs messages <run-id> [message]
```

Require an unambiguous run selection. Stop revokes dispatch and signals owned process trees. Resume reconciles state before retrying; never assume an orphaned provider stopped. Late results cannot integrate after stop or lease replacement.

## Evidence

Use real repository checks through validated check IDs and exact argv. Separate lightweight checks from full suites and builds. Keep one integration owner for shared files and lockfiles. Respect browser and simulator availability, existing user resource use, and configured parallelism. Say when a capability is unavailable instead of simulating it.

## Writing

Before writing plans, questions, status updates, review findings or delivery summaries, apply the shared [unslop writing rules](../hyperflow-plan/references/unslop.md). Preserve technical meaning and evidence.

For React Native or Expo work, load the shared [mobile and Vercel React Native guidance](../hyperflow-crash/references/browser-mobile.md) before assigning tasks or accepting changes. Use the active harness for available device and profiling tools.
