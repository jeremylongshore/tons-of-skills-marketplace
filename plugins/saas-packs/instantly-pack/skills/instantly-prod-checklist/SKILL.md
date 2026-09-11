---
name: instantly-prod-checklist
description: >-
  Gate an Instantly integration release across identity, scopes, data, limits, operations, and rollback. Use when reviewing a production launch or material campaign-system change for approval. Trigger with "review Instantly launch readiness", "run the Instantly release checklist", or "approve an Instantly production change".
argument-hint: "[release-sha] [workspace]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- prod-checklist
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Instantly Production Readiness Gate

## Overview

Return a fail-closed readiness decision backed by test and approval evidence. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- A green deploy is not authorization to activate campaigns or connect accounts.
- Keys, workspace-group delegation, webhook delivery, background jobs, and endpoint limits need explicit owners.
- Dynamic plan and entitlement facts must be rechecked at launch.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Verify release SHA, runtime, SDK/CLI pins, schema source, and rollback artifact.
2. Verify workspace identity, least-privilege keys, rotation, audit, and secret storage.
3. Verify consent, suppression, minimization, redaction, retention, and deletion controls.
4. Verify workspace and endpoint limits, pagination, batching, idempotency, and job polling.
5. Verify dashboards, alerts, incident runbook, webhook recovery, and support evidence.
6. List every unresolved gate and require accountable approval for launch and each data-plane mutation.

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
release=abc123; workspace=prod-opaque; launch=false
```

Expected handoff:

```text
decision=NO-GO; open-gates=2; owners=assigned
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
