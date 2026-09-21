---
name: palantir-local-dev-loop
description: >-
  Run a safe Foundry development loop using the Palantir VS Code extension, unit tests, preview/debug, repository synchronization, and remote builds. Use when iterating on transforms or OSDK code. Trigger with "Foundry local development".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[code-repository-or-application]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, local-development, testing]
---
# Palantir Local and In-Platform Development Loop

## Overview

Keep pure logic fast and local while treating Foundry preview, checks, and builds as separate evidence. A local mock can verify application logic, but it cannot prove Foundry permissions, lineage, transactions, or full-data behavior.

## Prerequisites

- Identify the Code Repository or Developer Console application, language, branch, data sensitivity, and target environment.
- Install the supported Palantir VS Code extension or use an in-platform workspace as appropriate.
- Read `references/official-docs.md` and the repository's generated in-platform documentation.
- Prepare lightweight unit fixtures without production data and a sandbox branch.

## Current Contract

- Foundry Code Repositories support sandbox branches, automatic checks, unit tests, previews, pull requests, and full builds.
- Preview can use sample or subset data; a full build runs on platform data and commits pipeline output.
- The VS Code extension can preview, debug, synchronize, and initiate Foundry builds from a local workspace.
- Local tests should isolate business logic and avoid relying on live external resources.

## Authentication

Use the approved Palantir VS Code or Developer Console sign-in for the intended environment. Keep generated OAuth settings and any test credentials in approved local secret storage, and never place tokens or production object data in fixtures, logs, or repository files.

## Instructions

1. Separate pure transformation or application logic from Foundry adapters and generated SDK code.

2. Write deterministic unit tests using synthetic fixtures and run them before any platform request.

3. Synchronize the sandbox branch, run Foundry checks, and preview representative inputs with protected-data rules intact.

4. Use the Foundry debugger for Python transform behavior when needed; treat observed values as diagnostic only.

5. Push the exact branch, run the full Foundry build or bounded OSDK smoke test, inspect results, and open a reviewed pull request.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

Local iteration does not authorize production data access, writeback, full builds, or merges. Obtain data-owner approval for representative protected inputs and repository-owner approval for merge or production build.

## Output

A reproducible development command map, synthetic fixtures, unit-test evidence, branch/commit, preview/debug findings, Foundry check/build results, and known differences between local, preview, and full execution.

## Error Handling

| Condition | Response |
|---|---|
| Local tests pass but Foundry checks fail | Use the repository check details and compare dependency/build environments. |
| Preview passes but full build fails | Inspect full-data edge cases, resources, and input transactions; preview is not production proof. |
| Generated OSDK mocks drift | Regenerate from Developer Console and update contract tests against the pinned package. |
| Debugger output differs from committed data | Treat debugger state as non-authoritative and verify the actual output transaction. |

## Examples

### Example 1

Refactor a transform so its row-level normalization is a pure function covered by synthetic unit tests, then run Foundry preview and a branch build to verify dataset integration.

### Example 2

Mock a generated OSDK client for application unit tests, then run a bounded non-production smoke test to prove OAuth restrictions, object selection, and pagination.

## Validation

- Unit fixtures contain no protected production data.
- The sandbox branch and local workspace are synchronized at one exact commit.
- Foundry checks and the relevant full build or smoke test pass.
- Preview limitations and environment differences are documented.
- The pull request receives the required independent review.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
