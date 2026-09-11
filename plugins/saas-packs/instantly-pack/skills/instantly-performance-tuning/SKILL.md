---
name: instantly-performance-tuning
description: >-
  Analyze and tune Instantly API v2 concurrency, pagination, batching, and retries against documented workspace limits. Use when operating performance tuning workflows. Trigger with "instantly performance tuning", "Instantly API", or "Instantly integration".
argument-hint: "[workload] [target-duration]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- performance-tuning
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Instantly Throughput Engineering

## Overview

Increase throughput without violating workspace or endpoint-specific limits or duplicating mutations. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- The general ceiling is 100 requests per second and 6,000 per minute per workspace across v1/v2 and keys.
- Endpoint-specific limits override the general ceiling.
- Bulk lead addition accepts up to 1,000 leads per request; asynchronous jobs require polling.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Measure route mix, payload sizes, current latency, 429s, and shared workspace traffic.
2. Classify reads, idempotent writes, non-idempotent writes, bulk operations, and background jobs.
3. Implement a workspace-wide token bucket below both general ceilings.
4. Honor endpoint overrides, jitter retryable reads, and never blindly retry non-idempotent mutations.
5. Use cursor pagination and documented bulk endpoints with bounded page/job polling.
6. Load-test synthetic staging data and publish before/after evidence plus rollback thresholds.

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
workload=lead-import; rows=10000; workspace-rps-budget=80
```

Expected handoff:

```text
batch=1000; concurrency=measured; duplicate-writes=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
