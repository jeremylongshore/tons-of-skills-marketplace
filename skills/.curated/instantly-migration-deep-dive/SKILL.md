---
name: instantly-migration-deep-dive
description: >-
  Plan and execute a governed Instantly API v1-to-v2 migration with endpoint and key inventory. Use when replacing deprecated v1 calls and incompatible keys before cutover. Trigger with "migrate Instantly v1 to v2", "inventory deprecated Instantly endpoints", or "plan an Instantly API cutover".
argument-hint: "[inventory-path] [phase]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- migration-deep-dive
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Instantly API v1-to-v2 Cutover

## Overview

Move a production integration from deprecated API v1 to incompatible API v2 without silent behavior drift. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- API v1 was deprecated on January 19, 2026; new integrations use API v2.
- API v2 needs a new scoped bearer key and is not compatible with v1 keys.
- Methods, paths, field naming, pagination, and several asynchronous operations changed.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Inventory every v1 endpoint, key, consumer, schedule, owner, and failure policy.
2. Map each call to the official migration table and required v2 scope.
3. Build v2 request/response contract tests for methods, snake_case fields, cursors, and background jobs.
4. Issue separate v2 keys and dual-read only where privacy and consistency controls allow it.
5. Canary one workflow, compare outcomes, then cut over consumers in bounded phases.
6. Retire v1 credentials only after rollback expiry and verified v2 stability.

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
phase=plan; calls=37; cutover=false
```

Expected handoff:

```text
mapped=37/37; tests=prepared; canary=awaiting-owner
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
