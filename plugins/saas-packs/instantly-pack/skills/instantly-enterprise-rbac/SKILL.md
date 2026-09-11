---
name: instantly-enterprise-rbac
description: >-
  Govern Instantly workspace members, API-key scopes, audit logs, and workspace-group delegation. Use when reviewing access or preparing an owner-approved membership, role, or delegated-workspace change. Trigger with "audit Instantly access", "review Instantly API scopes", or "delegate an Instantly workspace".
argument-hint: "[workspace-id] [review|change]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- enterprise-rbac
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Instantly Workspace Access Governance

## Overview

Review and change access with least privilege, explicit ownership, and tenant-boundary evidence. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- API v2 keys support granular resource/action scopes and can be revoked.
- Workspace groups let an admin key act for a sub-workspace through x-as-workspace.
- Only owners/admins can manage group membership, and only owners can leave a group.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Inventory members, roles, API keys, scopes, service owners, and last-use evidence.
2. Map each automation to the narrowest read/create/update/delete scope set.
3. Review audit logs and flag orphaned, broad, shared, or cross-workspace credentials.
4. For sub-workspace actions, validate the target ID and x-as-workspace header before execution.
5. Prepare member/key/group changes as a reviewed change set.
6. Apply only approved changes and verify both intended access and denied cross-tenant access.

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
mode=review; workspace=opaque-id; include-secrets=false
```

Expected handoff:

```text
broad-keys=2; orphaned-members=1; changes=awaiting-owner
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
