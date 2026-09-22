---
name: linear-webhooks-events
description: >-
  Implement Linear webhook verification, fast acknowledgement, deduplication, queued processing, and reconciliation. Use when receiving issue, project, cycle, customer, user, or OAuth-app events. Trigger with "handle Linear webhooks", "verify Linear signature", or "process Linear events".
argument-hint: "[repository-path] [framework] [event-types]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- webhooks
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Verified Webhook Processing

## Overview

Build an ingress path that proves authenticity on raw bytes, acknowledges quickly, and makes downstream processing replay-safe.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- The endpoint must be public HTTPS and return HTTP 200 within five seconds; failures retry after one minute, one hour, and six hours, up to three retries.
- `Linear-Signature` is the hex HMAC-SHA256 of the exact raw body; `Linear-Delivery` is the unique delivery UUID and `Linear-Timestamp` is epoch milliseconds.
- Only workspace admins or OAuth applications with `admin` scope can create or read webhooks.
- The official SDK provides `LinearWebhookClient`, including raw-body signature verification and framework handlers.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Select explicit resource types and team/all-public-team scope, and identify the webhook/admin owner.
2. Capture the exact raw request bytes before JSON middleware and verify HMAC-SHA256 with the configured signing secret.
3. Reject invalid or stale/replayed requests, deduplicate by `Linear-Delivery`, enqueue the verified envelope, and return 200 within five seconds.
4. Process events idempotently using `action`, `type`, entity ID, `updatedFrom`, organization, and webhook ID as appropriate.
5. Bound retries and dead-letter handling; never assume Linear will retry beyond the documented schedule.
6. Run periodic cursor-based reconciliation and test create/update/remove, duplicate, delayed, revoked-app, and secret-rotation cases.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| Signature mismatch | Return non-200, do not parse into business logic, and verify raw-body/secret selection. |
| Processing exceeds five seconds | Queue after verification and acknowledge before doing business work. |
| Duplicate delivery | Return 200 after recording the dedupe hit; do not repeat side effects. |
| Webhook disabled | Repair the endpoint, manually re-enable after approval, then reconcile the missed interval. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
scope=team; events=Issue,Comment; raw-body=true; queue=durable
```

Expected handoff:

```text
signature=verified; ack<5s; dedupe=delivery-id; reconciliation=enabled
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
