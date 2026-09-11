---
name: lucidchart-local-dev-loop
description: 'Run a fast, secretless local development loop for Lucid editor extensions and data connectors using official tooling. Use when implementing or debugging Lucid integrations. Trigger with "run Lucid locally".'
argument-hint: "[project-path] [test-focus]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, lucidchart, local-development, extension-sdk, testing]
model: inherit
effort: medium
compatibility: Designed for Claude Code; developer-mode installation and any live source connection require approval from the project and data owners
---
# Lucid Local Development Loop

## Overview
Establish a repeatable edit-build-test loop for an existing Lucid extension or connector, grounded in the installed project and official `lucid-package` tooling.

## Prerequisites
- A local project with lockfile, manifest, and documented runtime versions
- Synthetic fixtures and no production credentials by default
- A disposable Lucid developer test target when UI verification is needed

## Tool Discipline
Use `Read`, `Glob`, and `Grep` to inspect the project, `WebFetch` for official CLI/SDK guidance, and `Write` or `Edit` only for scoped source, fixture, test, or local documentation changes.

## Current Contract
Lucid maintains `lucid-package` and `lucid-extension-sdk`. Project scripts and installed CLI `--help` define the exact runnable commands; official guidance warns against guessing SDK types or pnpm argument syntax.

## Authentication
Keep the default loop offline and fixture-driven. Developer-mode access uses a dedicated least-privilege identity; connector/source secrets remain in an approved local secret provider and never enter bundles or snapshots.

## Instructions
1. Read repository instructions, manifest, package manager, lockfile, scripts, SDK versions, and test configuration.
2. Query installed command help and compare it with current official CLI and SDK documentation.
3. Select the narrowest loop: type/build, manifest validation, unit fixture, connector contract, or editor smoke test.
4. Run the existing deterministic command before editing and preserve its receipt.
5. Make one bounded change, rerun the narrow check, then run all affected local gates.
6. For developer-mode testing, preview scopes, bundle identity, test document, and expected mutations before installation.
7. Record command, duration, changed files, fixture digest, expected/actual result, and cleanup.

## Approval Boundaries
Do not add dependencies, install into a Lucid account, contact a live source, or change registered application settings without approval.

## Output
Return environment/version evidence, selected loop, commands, test receipts, changed files, developer-mode actions, cleanup, and remaining drift.

## Error Handling
| Condition | Response |
|---|---|
| Project command and docs disagree | Trust installed help/project scripts, investigate version drift, and document it. |
| Test requires production data | Replace it with a representative synthetic fixture. |
| Developer installation mutates unexpected data | Stop, capture evidence, and remove the test artifact if approved. |

## Example
```text
focus=extension-build; package-manager=pnpm; fixture-sha256=...; narrow=pass; affected-gates=pass; live-data=no
```

## Resources
- [Official documentation map](references/official-docs.md)

## Next Steps
Encode the proven commands in CI with the same pinned runtime, lockfile, and synthetic fixtures.
