---
name: instantly-multi-env-setup
description: >-
  Separate Instantly development, staging, and production workspaces, keys, data, and webhook routes. Use when designing environment isolation or eliminating shared credentials and callbacks. Trigger with "separate Instantly environments", "create an Instantly staging workspace", or "isolate Instantly webhook routes".
argument-hint: "[environment-map-path]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- multi-env-setup
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Instantly Multi-Environment Isolation

## Overview

Design environment isolation and promotion without fake vendor endpoints or accidental cross-workspace mutations. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- Use separate workspaces and keys where isolation requirements demand it.
- Workspace-group delegation uses x-as-workspace and increases cross-tenant risk.
- Environment names are not proof of identity; validate opaque workspace IDs and read-only probes.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Document environment-to-workspace IDs, owners, scopes, data classes, domains, and webhook URLs.
2. Use local fakes for development and synthetic records for staging.
3. Store one scoped key reference per environment; never use fallback production credentials.
4. Add startup guards that compare the expected opaque workspace ID before mutation.
5. Promote code and schemas separately from campaigns, leads, accounts, or webhooks.
6. Test denied cross-environment access and maintain a credential and webhook rollback plan.

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
dev=local-fake; staging=workspace-a; prod=workspace-b
```

Expected handoff:

```text
isolation=verified; fallback-keys=0; mutations=separate-change
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
