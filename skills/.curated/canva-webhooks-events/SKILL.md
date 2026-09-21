---
name: canva-webhooks-events
description: 'Implement Canva preview webhook verification, routing, replay defense, and idempotent processing. Use when receiving supported notification types in a non-public or otherwise eligible integration. Trigger with: "Canva webhook", "verify Canva signature", "handle Canva notification".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[notification-types-and-callback-url]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - webhooks
  - operations
compatibility: 'Canva webhooks and keys are preview; Canva states public integrations using preview features cannot pass review.'
---

# Canva Preview Webhook Intake

## Overview

Authenticate every notification with Canva's rotating public JWK set, then apply separate tenant/resource authorization and idempotency. Webhooks are outgoing-only and do not replace the Comments API for replies.

## Prerequisites

- Eligible integration and explicitly approved preview use
- Controlled HTTPS callback, required scopes, and notification allowlist
- Durable idempotency store, queue, retention, and incident owner

## Instructions

### Step 1: Confirm eligibility

Use Read and Grep to verify current preview status, public-review posture, required collaboration plus notification-specific scopes, and enabled notification types.

### Step 2: Fetch and cache keys

Use the public unauthenticated connect/keys endpoint, cache the rotating Ed25519/OKP JWK set, select by case-sensitive key ID, and refetch only once for an unknown key.

### Step 3: Verify before parsing actions

Validate signature and documented token claims, reject wrong issuer/audience/time/context, cap request size, and retain no raw signed token in logs.

### Step 4: Defend against replay

Create a durable idempotency key from the verified notification identity, enforce an application retention window, and acknowledge duplicates without repeating effects.

### Step 5: Authorize the event

Resolve tenant, user/resource ownership, notification type, feature status, and application policy. A valid signature does not authorize a write or reply.

### Step 6: Queue and process

Use Write or Edit to persist only approved fields and enqueue after verification. Return the protocol response required by the current docs without waiting on downstream side effects.

### Step 7: Reconcile and observe

Record verification class, normalized type, duplicate state, queue result, redacted error, and handler version; dead-letter safely and require owner-reviewed replay.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

A verified comment notification is deduplicated and routed to an authorized tenant queue. Any response comment is sent separately through the current Comments API after its own policy check.

## Error Handling

| Failure | Response |
| --- | --- |
| Preview is ineligible for release | Disable the webhook path |
| Key ID is unknown | Refresh keys once and fail closed if unresolved |
| Notification type is unrecognized | Quarantine metadata only and update the contract |
| Duplicate delivery arrives | Acknowledge without replaying side effects |

## Resources

- [First-party source notes](references/official-docs.md)
- [Webhooks](https://www.canva.dev/docs/connect/webhooks/)
- [Webhook keys](https://www.canva.dev/docs/connect/api-reference/webhooks/keys/)
