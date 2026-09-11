---
name: instantly-webhooks-events
description: >-
  Analyze and register and operate Instantly webhooks with schema validation, idempotency, privacy, and recovery controls. Use when operating webhooks events workflows. Trigger with "instantly webhooks events", "Instantly API", or "Instantly integration".
argument-hint: "[receiver-url] [event-set]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- webhooks-events
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Instantly Webhook Operations

## Overview

Build a receiver for documented Instantly event types without assuming an unpublished signature or retry contract. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- Events include workspace, campaign, timestamp, event_type, and optional lead/email/reply content.
- Custom labels may arrive as event_type values.
- The API supports list, create, patch, delete, test, resume, event-type discovery, and delivery-event observability.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Fetch the live event-type list and select only required events.
2. Review the HTTPS destination, data classification, retention, and receiver owner.
3. Create the webhook with the exact documented fields and least-privilege scope.
4. Validate schema, workspace identity, timestamp bounds, payload size, and event-specific optional fields.
5. Deduplicate using a receiver-owned stable fingerprint and process asynchronously.
6. Use test, delivery-event aggregates, and resume only with explicit change approval.

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
events=email_bounced,reply_received; receiver=https://example.invalid/hook
```

Expected handoff:

```text
registration=planned; signature=not-assumed; approval=required
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
