---
name: attio-local-dev-loop
description: >-
  Establish a repeatable local Attio development loop with sanitized fixtures, a non-production workspace, explicit mutation switches, and cleanup receipts. Use when iterating on Attio mappings or API behavior. Trigger with "Attio local development", "Attio dev loop", or "test Attio locally".
argument-hint: "[repository-path] [workspace-alias]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- attio
- development
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Attio Local Development Loop

## Overview

This skill makes local iteration fast without turning a shared CRM into a test fixture. Offline contracts are the default; live writes are explicit and disposable.

## Prerequisites

- A named repository and test runner
- Sanitized success and error fixtures
- A development Attio workspace or approved test boundary
- A cleanup ledger for any live records or entries

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect environment loading, client boundaries, fixtures, and tests. Use `WebFetch` only for current official Attio documentation. Use `Write` or `Edit` after confirming the repository path and test-data policy.

## Current Contract

- Keep offline request/response contracts separate from live integration tests.
- Never copy production CRM payloads into fixtures.
- Guard live mutation behind an explicit switch and exact workspace allowlist.
- Pagination fixtures must match the selected endpoint's offset or cursor contract.

## Authentication

Use a least-privilege development workspace token from local secret injection. Do not place the token in a committed environment file, fixture, command transcript, or snapshot.

## Instructions

1. Locate the Attio client boundary, mappings, retry policy, and existing fixture conventions.
2. Define sanitized fixtures for success, validation failure, authorization failure, throttling, and pagination termination.
3. Add a local configuration guard that identifies the workspace and disables writes by default.
4. Run the smallest offline test while editing mappings or response normalization.
5. When live behavior is necessary, display the workspace and disposable target before enabling one bounded operation.
6. Record created resource IDs in the cleanup ledger, clean them up after review, and verify absence.

## Approval Boundaries

Live writes, schema changes, bulk operations, and cleanup deletes require an approved non-production target. If workspace identity cannot be proved, remain offline.

## Output

Return the fixture matrix, local commands, workspace guard, offline results, live-test disposition, created-resource ledger, and cleanup evidence.

## Error Handling

| Condition | Response |
|---|---|
| Fixture contains real CRM data | Remove and regenerate it from synthetic values. |
| Workspace allowlist fails | Keep writes disabled. |
| Live response drifts | Update the contract deliberately after documentation review. |
| Cleanup fails | Stop further writes and report exact disposable IDs. |

## Examples

Input:

```text
mode=offline-first; workspace=development; live-writes=disabled
```

Expected handoff:

```text
fixtures=pass; guard=pass; live-test=not-needed; leaked-data=0
```

This result demonstrates a repeatable development cycle without production data or mutations.

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [REST API overview](https://docs.attio.com/rest-api/overview)
- [Pagination](https://docs.attio.com/rest-api/guides/pagination)
- [Creating an Attio app](https://docs.attio.com/sdk/guides/creating-an-app)
