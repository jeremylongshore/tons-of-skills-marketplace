---
name: instantly-rate-limits
description: >-
  Implement Instantly API v2 workspace-wide throttling, endpoint overrides, and safe 429 recovery. Use when operating rate limits workflows. Trigger with "instantly rate limits", "Instantly API", or "Instantly integration".
argument-hint: "[service] [workspace-budget]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- rate-limits
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Instantly Workspace Rate Control

## Overview

Coordinate traffic across clients and keys so retries do not amplify throttling or duplicate writes. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- General limits are 100 requests per second and 6,000 per minute across API v1/v2 for the whole workspace.
- GET /emails is limited to 20 requests per minute; other endpoints may publish independent limits.
- 429 is the authoritative throttling signal; retry timing must follow documented or observed response metadata.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Inventory every producer sharing the workspace and every endpoint-specific override.
2. Allocate a workspace request budget below both general windows.
3. Centralize token-bucket state and expose queue depth, wait time, and 429 telemetry.
4. Retry only operations proven safe, with bounded exponential backoff and jitter.
5. Do not assume a webhook retry count or timing absent a published contract.
6. Test burst, sustained, override, and retry-storm scenarios with synthetic traffic.

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
workspace-rps=80; workspace-rpm=4800; email-list-rpm=15
```

Expected handoff:

```text
limits=enforced; retry-budget=bounded; mutation-retries=disabled
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
