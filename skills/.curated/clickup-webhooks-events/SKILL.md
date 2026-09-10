---
name: clickup-webhooks-events
description: >-
  Register, verify, process, monitor, and reconcile ClickUp webhooks with raw-body HMAC, durable idempotency, fast acknowledgment, and gap recovery. Use when building event-driven ClickUp integrations. Trigger with "ClickUp webhook", "verify X-Signature", or "ClickUp events".
argument-hint: "[workspace-id] [endpoint-url] [plan|apply]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- webhooks
model: inherit
effort: high
compatibility: Designed for Claude Code; registration requires authorized ClickUp access and public HTTPS ingress
---
# ClickUp Signed Webhook Operations

## Overview

Treat webhooks as signed, user-owned change signals that need durable processing and reconciliation. Assume delivery can duplicate, arrive late, or stop after ownership changes.

## Prerequisites

- A public HTTPS endpoint capable of retaining raw request bytes
- A secret manager, durable queue/idempotency store, and Workspace allow-list
- An authorized user owner for the webhook plus monitoring and reconciliation

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- Webhook creation returns a unique secret; verify raw-body HMAC-SHA256 against hexadecimal `X-Signature`.
- Registrations are tied to the creating user and can stop triggering when that user is disabled or loses hierarchy access.
- Use `webhook_id:history_item_id` as the documented idempotency key when a history item exists; handle events without one deliberately.
- Responses over seven seconds or unsuccessful responses are failures; ClickUp attempts delivery up to five times, does not resend the failed event later, suspends at `fail_count=100`, and a 401 suspends immediately.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Choose the narrowest location and explicit event set; inventory duplicate registrations before creation.
2. Register only after endpoint ownership, HTTPS, secret storage, and rollback approval are confirmed.
3. Capture raw bytes, look up the per-webhook secret, verify HMAC in constant time, then parse/validate JSON.
4. Persist idempotency and enqueue before a fast success response; process business effects asynchronously.
5. Monitor status/fail count, latency, duplicates, dead letters, and owner eligibility.
6. Run reconciliation reads for delivery gaps and rotate/re-register safely when ownership changes.

## Approval Boundaries

Require approval before creating, broadening, suspending/reactivating, rotating, or deleting production webhooks and before replaying business effects.

## Output

Return the registered scope, credential-storage identifier, HMAC verification and idempotency test results, delivery health, queue result, reconciliation status, and rollback.

## Error Handling

| Condition | Response |
|---|---|
| Signature invalid | Reject before parsing and record content-free evidence. |
| Handler cannot persist within deadline | Return failure deliberately and repair capacity; do not acknowledge lost work. |
| Webhook suspended | Contain, diagnose fail count/401 behavior, and reactivate only after approval. |
| History item is absent | Use a documented event-specific fallback key and reconciliation. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
events=taskUpdated,taskDeleted; hmac=pass; ack=82ms; duplicate=ignored; fail-count=0; reconcile=pass
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Webhooks](https://developer.clickup.com/docs/webhooks)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
