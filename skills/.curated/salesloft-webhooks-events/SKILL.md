---
name: salesloft-webhooks-events
description: >-
  Verify and process Salesloft webhooks using exact raw-body SHA-1 HMAC, callback-token validation, event routing, durable deduplication, and reconciliation. Use when building or auditing a webhook receiver. Trigger with "Salesloft webhook", "Salesloft signature", or "Salesloft event handler".
argument-hint: "[repository-path] [event-type]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- salesloft
- webhooks
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Salesloft Verified Webhook Processing

## Overview

This skill accepts a delivery only after authenticating its exact bytes and subscription secret. It makes side effects idempotent even though the general delivery contract does not expose a timestamp replay header.

## Prerequisites

- Approved HTTPS callback URL and event type
- Webhook subscription with a high-entropy callback token
- Raw-body access before JSON parsing
- Durable deduplication store and reconciliation owner

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect body parsing, signature comparison, queues, and side effects. Use `WebFetch` only for current official Salesloft webhook documentation. Use `Write` or `Edit` after the handler boundary is confirmed.

## Current Contract

- `x-salesloft-event` identifies the delivered event type.
- `x-salesloft-signature` is the hexadecimal SHA-1 HMAC of the exact response/request body using `callback_token` as the key.
- The callback token is also included in each event payload and should be validated.
- Failed deliveries are retried three additional times, 15 seconds apart.
- Subscription scopes vary by event type and must be checked in the current event table.

## Authentication

Protect the callback token as a secret. Compute the expected HMAC from the exact raw body, decode hex safely, require equal lengths, and use constant-time comparison before parsing or queuing.

## Instructions

1. Capture raw bytes and required headers before any middleware transforms the body.
2. Reject missing, malformed, unequal-length, or non-matching signatures.
3. Parse JSON only after signature success and validate the callback token and expected event type.
4. Derive a stable deduplication key from event type plus canonical business identifiers and payload digest.
5. Persist receipt and dedup state before acknowledging or dispatching side effects.
6. Process asynchronously with bounded retries and reconcile missed changes through API reads.
7. Test tampering, malformed hex, duplicate delivery, retry, queue failure, and rotated token behavior.

## Approval Boundaries

Do not create or change a subscription, callback URL, event scope, or production token without owner approval. Reject unverifiable events rather than accepting them for debugging convenience.

## Output

Return event type, signature and callback-token verdicts, dedup key, queue receipt, processing result, retry state, and reconciliation status without payload data.

## Error Handling

| Condition | Response |
|---|---|
| Signature mismatch | Reject before parsing and record redacted metadata. |
| Duplicate delivery | Return prior outcome without repeating side effects. |
| Handler failure | Preserve receipt and use bounded internal retry. |
| Missed event suspected | Reconcile through the relevant read endpoint or cursor poller. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
event=person_updated; signature=pass; callback-token=pass; duplicate=no; queued=yes
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Webhook delivery headers](https://developers.salesloft.com/docs/platform/webhooks/delivery-headers/)
- [Webhook event types](https://developers.salesloft.com/docs/platform/webhooks/event-types/)
- [Create a webhook subscription](https://developers.salesloft.com/docs/api/webhook-subscriptions-create/)
