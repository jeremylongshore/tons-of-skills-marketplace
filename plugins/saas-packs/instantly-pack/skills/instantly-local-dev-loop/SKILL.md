---
name: instantly-local-dev-loop
description: >-
  Build an offline-first Instantly development loop with fixtures, fakes, and optional read-only staging probes. Use when developers need fast repeatable tests without mutating a live workspace. Trigger with "mock the Instantly API", "build Instantly fixtures", or "test Instantly locally".
argument-hint: "[repository-path] [offline|staging]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- local-dev-loop
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Instantly Local Contract Loop

## Overview

Develop safely without relying on an undocumented vendor mock endpoint or sending real outreach. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- The documentation exposes interactive examples but does not establish a durable public mock API contract.
- Use local fakes and captured synthetic schemas for deterministic tests.
- Live probes require a staging workspace, read-only scopes, and bounded requests.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Inventory routes and generate or pin types from the official OpenAPI surface.
2. Create local fake responses for success, 401, 403, 429, pagination, and malformed data.
3. Use synthetic leads and messages; never copy production payloads into fixtures.
4. Run unit and contract tests without network access.
5. Optionally run one owner-approved read-only staging probe.
6. Update fixtures only after reviewed schema evidence and record the source date.

## Approval Boundaries

Do not create, rotate, reveal, or revoke keys; invite or remove members; delegate across workspaces; connect sending accounts; create or activate campaigns; import or delete leads; change suppression or retention; register, patch, resume, or delete webhooks; alter plans or paid capacity; transmit diagnostics; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace-safe scope, files and contracts inspected, exact API v2 routes and required scopes, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| `401` | Stop and verify that the bearer key exists, is current, and was not revoked. |
| `403` | Stop and compare the operation with its exact required scope; do not broaden to `all:all` by default. |
| `429` | Coordinate the workspace-wide budget, honor endpoint overrides, and bound retries. |
| Schema or tenant mismatch | Fail closed, preserve redacted evidence, and do not retry a mutation. |

## Examples

Use a compact handoff that makes scope, mutation authority, and evidence reviewable.

Input:

```text
mode=offline; fixture=campaign-list; network=false
```

Expected handoff:

```text
unit=pass; contract=pass; staging=skipped
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
