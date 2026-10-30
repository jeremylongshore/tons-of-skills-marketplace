---
name: zero-tech-debt
description: >
  Refactor a feature toward its intended product architecture, removing obsolete
  flows and unnecessary abstractions while preserving required behavior and
  contracts. Use when a structural redesign or tech-debt cleanup is requested.
  Trigger with "refactor properly", "remove legacy" or "zero-tech-debt";
  use a focused patch for hotfixes and security backports.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git:*), Bash(rg:*), Bash(fd:*)
version: 1.2.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [refactoring, tech-debt, architecture, cleanup, modernization, code-quality]
user-invocable: true
---

# Zero Tech Debt

## Overview

Build toward the intended product shape rather than preserving the sequence of
historical patches. Keep one coherent end state in scope. Remove obsolete layers
when evidence supports removal; do not use smaller diffs or fewer files as a
substitute for the requested architecture.

Current code is evidence of behavior and contracts, not automatic architectural
authority. Explicit requirements, supported clients, persisted data, security
boundaries and the user's instructions still govern what may change.

## Prerequisites

- A requested feature or ownership boundary and a clear intended end state.
- Access to relevant code, tests, configuration, contracts and known consumers.
- The repository's change/review rules and existing task authorization.

Read [when to use this method](references/01-when-to-use.md) before choosing a
structural redesign. For an ambiguous "clean up" request, infer scope from the
context and ask only for a missing decision that materially affects the outcome.

## Instructions

1. Read [preflight](references/02-preflight-checklist.md). Establish the intended
   behavior, known callers, evidence gaps, recovery strategy and overlapping work.
   Scale verification to the actual change; do not demand exhaustive downstream
   access or new infrastructure for a reversible local rename.
2. Follow [the seven-step workflow](references/03-workflow.md): define the end
   state, audit reality, simplify existing paths, implement the final shape,
   consolidate decision ownership, align names and validate.
3. Use Glob to locate affected files and tests; use Grep or Bash(rg:_) to find
   callers, configuration, docs and telemetry dependencies. Bash(fd:_) is optional
   when installed. Read surrounding code rather than treating a name match as a
   removal instruction. Record search scope and inaccessible consumers.
4. Apply [audit patterns](references/04-audit-patterns.md) and
   [decision filters](references/05-decision-filters.md). Keep, delete, rename or
   defer each candidate according to actual responsibility and requirements.
   Single-implementation interfaces, adapters and versioned names can be useful.
5. Use Edit for scoped revisions and Write for needed new modules or tests. Keep
   the code coherent as the target structure changes. A replacement and its
   callers may belong in the same atomic change; do not force an intermediate
   broken state to satisfy a delete-before-add slogan.
6. Investigate failed tests against independent requirements and contracts before
   changing expectations. Add focused regression coverage where needed to protect
   behavior or changed boundaries; do not rewrite assertions just to fit the new
   implementation or add tests that merely mirror a simple edit.
7. Use Bash(git:\*) for permitted diff review, staging and normal scoped commits
   under repository rules. Preserve unrelated work. Refactor permission does not
   authorize destructive Git operations, deployment, outreach or data migration.
8. Report [outcomes and evidence](references/06-outcomes-and-reporting.md): what
   changed, why it matches the intended end state, what was verified and what
   remains uncertain. Do not promise zero future debt or unmeasured reliability gains.

## Output

A reviewable change implementing the agreed end state, with updated callers,
contracts, documentation or migrations where the scope requires them. Explain:

- The intended behavior and resulting architecture or ownership change.
- Removed, unified or renamed paths and their evidence-based rationale.
- Preserved compatibility or deferred work with a concrete reason.
- Actual validation results, evidence limits and recovery implications.

Use the project's issue tracker for durable follow-up work. Do not invent tickets,
caller counts, successful migration results or stakeholder approval.

## Error Handling

| Situation                         | Recovery                                                                                                                |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Intended behavior is unclear      | Inspect requirements and ask for the missing decision before a conflicting change.                                      |
| A caller cannot be inspected      | Record the uncertainty; retain compatibility or resolve the contract decision before removal.                           |
| A test fails after redesign       | Reproduce and compare with requirements; fix the regression or justify a separately supported expectation change.       |
| Another migration overlaps        | Coordinate through the authorized workflow or isolate independent work; do not overwrite it.                            |
| Data migration is irreversible    | Verify backup/restore or forward recovery in an authorized isolated environment; do not demand a destructive downgrade. |
| Deeper debt appears outside scope | Record the finding without silently expanding the refactor.                                                             |

## Examples

**Consolidate retry ownership:** "Replace the three divergent retry loops with one
policy." Inspect each loop's deadlines, retryable errors and idempotency behavior.
Build the requested common policy, update callers atomically and verify those
contracts; do not erase meaningful differences just to reduce the count.

**Remove a legacy export:** A repository search finds no callers, but an exported
package API is public. Record the search limits and resolve supported-client and
deprecation requirements before deletion. An empty search does not prove no usage.

**Redesign storage:** "Move this workflow to the new state model." Use an isolated,
authorized fixture or sanitized snapshot to check data mapping and recovery. Keep
production execution separate from the source refactor's authorization.

## Resources

- [Scope and non-triggers](references/01-when-to-use.md)
- [Proportionate preflight](references/02-preflight-checklist.md)
- [Seven-step workflow](references/03-workflow.md)
- [Audit patterns](references/04-audit-patterns.md)
- [Decision filters](references/05-decision-filters.md)
- [Outcomes and evidence](references/06-outcomes-and-reporting.md)
