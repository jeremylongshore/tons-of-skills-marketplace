---
name: instantly-hello-world
description: >-
  Run one bounded read-only Instantly API v2 request with explicit authentication and response validation. Use when verifying a new API key, workspace, or HTTP client before deeper integration work. Trigger with "test my Instantly API key", "make a first Instantly request", or "list Instantly campaigns safely".
argument-hint: "[accounts|campaigns] [limit]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- hello-world
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Instantly Bounded First Request

## Overview

Prove a new Instantly integration with the smallest safe request and a redacted evidence handoff. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- The API v2 base URL is https://api.instantly.ai/api/v2.
- Authorization uses an API v2 key as a Bearer token.
- A 401, 403, or 429 must fail the smoke test rather than trigger mutation or broad retries.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Confirm the target workspace and create a read-only key with accounts:read or campaigns:read.
2. Store the key in a server-side environment variable and never print it.
3. Send one list request with a limit no greater than five.
4. Validate HTTP status and expected collection/pagination fields.
5. Capture latency, status, route template, and redacted item count.
6. Stop after the proof; do not create, patch, activate, or delete resources.

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
resource=accounts; limit=5; workspace=staging
```

Expected handoff:

```text
status=200; items=bounded; auth=redacted; mutation=none
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
