---
name: palantir-ci-integration
description: >-
  Design and verify Foundry-native continuous-integration and review gates for Code Repositories and transforms. Use when a team needs branch checks, unit tests, dataset-impact review, or controlled promotion. Trigger with "Palantir CI" or "Foundry repository checks".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[code-repository-or-branch]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, ci, code-repositories]
---
# Palantir Foundry CI and Review Gates

## Overview

Build the quality gate around Foundry Code Repository branches, automatic checks, unit tests, and pull-request review. External Git hosting may mirror evidence, but it must not replace the checks that Foundry runs against repository inputs, outputs, dependencies, and platform builds.

## Prerequisites

- Identify the Foundry enrollment, Code Repository, target branch, owned datasets, and release owner.
- Confirm whether the repository uses Python transforms, TypeScript, or another supported project type.
- Read `references/official-docs.md` and inspect the repository's effective CI and branch settings before proposing changes.
- Use a sandbox branch and non-production data until the checks and rollback path are proven.

## Current Contract

- A commit to a Code Repository branch runs automatic checks; the Checks tab is the primary result surface.
- Python unit tests can participate in repository CI when configured according to the repository's supported build layout.
- Transform input and output declarations are evaluated by CI and cannot be chosen dynamically at build time.
- A pull request can require approving review before merge, and reviewers can inspect dataset impact for transform changes.

## Instructions

1. Inventory current branch protection, checks, unit-test wiring, build ownership, and required reviewers.

2. Create or update tests so each test isolates one unit of transform logic and avoids live external dependencies.

3. Run the Foundry branch checks and preserve the exact failing check, build report, and dependency evidence.

4. Open a Foundry pull request, review code plus dataset impact, and obtain the required independent approval.

5. Merge only the exact reviewed commit, then verify the main-branch checks and downstream build behavior.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

Require the Code Repository owner to approve branch-policy changes and the data owner to approve changes to dataset inputs, outputs, or production builds. Do not bypass a failed Foundry check or approving-review requirement.

## Output

A CI gate map containing repository, branch, checks, tests, dataset impact, reviewers, exact commit, result links, and rollback. Separate Foundry evidence from any external Git mirror or notification evidence.

## Error Handling

| Condition | Response |
|---|---|
| A check fails only in Foundry | Compare preview inputs with full-build inputs, dependency resolution, ownership, and the detailed build report. |
| A branch is behind | Upgrade or merge the required base changes on the sandbox branch, then rerun all checks. |
| A required dataset is not owned | Stop and resolve project/resource ownership; do not weaken the check. |
| External CI is green but Foundry is red | Treat the Foundry result as authoritative for Foundry execution and block merge. |

## Examples

### Example 1

Add a lightweight `pytest` suite to a Python transforms repository, prove it appears in the Foundry Checks tab, and require an approving Foundry pull-request review before merge.

### Example 2

Diagnose a transform that previews successfully but fails its full CI build by comparing the sampled preview with the production data, dependency set, and declared inputs.

## Validation

- Every required check is visible on the exact candidate commit.
- The unit tests run in the supported Foundry repository check path.
- Dataset inputs, outputs, owners, and lineage impact match the review record.
- The main branch repeats the expected checks after merge.
- The rollback commit or product version is identified before promotion.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
