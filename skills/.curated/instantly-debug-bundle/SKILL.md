---
name: instantly-debug-bundle
description: >-
  Collect a minimal redacted Instantly diagnostic bundle for campaigns, accounts, jobs, and webhook delivery. Use when operating debug bundle workflows. Trigger with "instantly debug bundle", "Instantly API", or "Instantly integration".
argument-hint: "[incident-id] [output-path]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- debug-bundle
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Redacted Instantly Diagnostic Bundle

## Overview

Gather reproducible operational evidence without exporting credentials, lead data, or message bodies. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- Use documented list, sending-status, vitals, background-job, and webhook-event aggregates.
- Raw lead, email, and webhook payloads may contain personal or message content.
- Support sharing is an external disclosure that needs owner review.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Define the failing operation, time window, workspace, incident owner, and evidence destination.
2. Collect client version, route templates, statuses, request IDs, and timestamps.
3. Query only aggregate campaign, account, job, and webhook health needed for the incident.
4. Replace workspace, campaign, account, lead, and email identifiers with stable opaque labels.
5. Scan the bundle for bearer tokens, addresses, message text, and unrestricted environment output.
6. Present the manifest and obtain approval before transmitting it outside the team.

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
incident=INC-123; window=30m; include-bodies=false
```

Expected handoff:

```text
bundle=diagnostics.json; identifiers=tokenized; disclosure=not-sent
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
