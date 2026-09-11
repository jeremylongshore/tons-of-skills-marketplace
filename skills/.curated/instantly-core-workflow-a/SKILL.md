---
name: instantly-core-workflow-a
description: >-
  Build and launch an Instantly API v2 campaign through an approval-gated, reversible workflow. Use when creating a campaign from a reviewed audience, schedule, and sequence specification. Trigger with "create an Instantly campaign", "launch an Instantly sequence", or "build campaign from spec".
argument-hint: "[campaign-spec-path] [workspace]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- core-workflow-a
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Governed Instantly Campaign Launch

## Overview

Create a campaign from reviewed inputs, load approved leads, validate sending state, and require explicit activation approval. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- Campaigns use REST API v2 resources and scoped keys.
- Lead listing is POST /leads/list because filters are complex; bulk lead addition supports at most 1,000 leads per request.
- Campaign activation is a separate mutation and must not be implicit in creation.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Read the campaign specification, consent basis, suppression rules, sending accounts, schedule, and rollback owner.
2. Resolve workspace identity and use campaigns/leads scopes no broader than required.
3. Create or patch a draft campaign with bounded sequences and approved variables.
4. Import a small deduplicated synthetic or approved lead cohort and inspect rejected rows.
5. Validate campaign sending status, account health, schedule, and compliance gates.
6. Present the exact activation action and execute it only after explicit approval.

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
campaign=draft; leads=25-approved; activate=false
```

Expected handoff:

```text
draft=created; validation=pass; activation=awaiting-owner
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
