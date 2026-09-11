---
name: instantly-data-handling
description: >-
  Analyze and govern Instantly lead, email, suppression, export, and deletion data with explicit privacy controls. Use when operating data handling workflows. Trigger with "instantly data handling", "Instantly API", or "Instantly integration".
argument-hint: "[data-flow-path] [workspace]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- data-handling
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Instantly Lead Data Governance

## Overview

Map and constrain personal-data movement across lead ingestion, campaigns, webhooks, exports, logs, and deletion. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- Lead payload values may be scalar values; nested arrays are not a safe assumed contract.
- Webhook payloads can contain lead and full reply/email content.
- Deletion and export behavior must be tied to customer policy and signed terms, not generic assumptions.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Classify every input field, purpose, legal basis, retention owner, and downstream destination.
2. Map create, list, patch, export, webhook, and delete paths with exact scopes.
3. Minimize payloads and apply blocklist, consent, suppression, and deduplication controls before import.
4. Redact email bodies, reply text, API keys, and personal identifiers from logs and evidence.
5. Test access, correction, suppression, export, and deletion with synthetic records.
6. Require privacy and data-owner approval before production retention or deletion changes.

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
dataset=synthetic-leads; fields=email,first_name; retention=policy-bound
```

Expected handoff:

```text
flow=mapped; minimization=pass; production-change=awaiting-owner
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
