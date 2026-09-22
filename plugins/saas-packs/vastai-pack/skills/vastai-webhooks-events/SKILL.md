---
name: vastai-webhooks-events
description: >-
  Analyze, verify, and operate Vast.ai notification webhooks with exact-body HMAC, replay protection, deduplication, durable enqueue, and failure-aware acknowledgment. Use when notification events must drive automation. Trigger with: "receive Vast.ai webhooks", "verify X-Vast-Signature-256", "handle duplicate Vast.ai events".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[client-or-host-event-keys-and-public-https-endpoint]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - webhooks
  - signatures
  - event-processing
compatibility: 'Requires a public HTTPS receiver, durable queue and deduplication store, secret manager, and notification webhook access.'
---

# Signed Vast.ai Notification Receiver

## Overview

Vast.ai notifications are signed, at-least-once deliveries. Verify the exact raw body before JSON parsing, reject stale timestamps, deduplicate by stable event ID, enqueue durably, and return success only after acceptance.

## Prerequisites

- Full subscription keys such as `client:low_credit` or `client:outbid`
- Public HTTPS endpoint without redirects or private-address resolution
- Webhook secret store, five-minute replay window, durable queue, and event ledger

## Instructions

### Step 1: Create a bounded subscription

Discover valid notification types and subscribe only the required full client or host keys. Respect the four-webhook-per-user limit and retain context-specific webhooks when short slugs overlap.

### Step 2: Store the one-time secret

Capture the signing secret at create or rotate time because list and update responses do not return it. Test retrieval and rotation ownership.

### Step 3: Verify raw delivery

Require POST, read exact body bytes, combine integer `X-Vast-Timestamp`, a period, and raw body, then compare the HMAC-SHA256 against `X-Vast-Signature-256` in constant time.

### Step 4: Reject replay and duplicates

Reject missing or malformed headers and timestamps older than 300 seconds. Deduplicate retries using `X-Vast-Event-Id` or payload `event_id`.

### Step 5: Acknowledge after durable enqueue

Persist the verified event and return 2xx quickly. Process side effects asynchronously and idempotently; the delivery timeout is ten seconds.

### Step 6: Test and operate failure paths

Use the provider test delivery, verify rotation, and monitor permanent 3xx/most-4xx failures versus retryable 408, 429, 5xx, timeout, or connection errors.

## Authentication

Webhook configuration uses the scoped Vast.ai API key; delivery verification uses the distinct webhook secret. Never log either secret or parse/re-serialize JSON before signature verification.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Subscription keys, webhook ID, and secret-rotation ownership
- Signature, replay, deduplication, enqueue, and idempotency tests
- Delivery health and retry/permanent-failure receipt

Return webhook ID, context keys, test event ID, signature/replay/dedupe results, acknowledgment latency, queue record, and rotation date.

## Examples

A `client:low_credit` delivery is verified from raw bytes, rejected if older than five minutes, deduplicated by event ID, enqueued, and acknowledged with 204 before the worker pages the billing owner.

## Error Handling

| Failure | Response |
| --- | --- |
| Signature or timestamp is invalid | Return a permanent client error and do not enqueue or disclose verification details. |
| Duplicate event arrives | Return success after confirming the original durable record; do not repeat side effects. |
| Queue is unavailable | Return a retryable failure such as 503 rather than acknowledging data loss. |
| Endpoint redirects | Fix the configured final HTTPS URL because redirects are permanent delivery failures. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Notification webhooks](https://docs.vast.ai/guides/reference/notification-webhooks)
- [List notification types](https://docs.vast.ai/api-reference/notifications/list-notification-types)
- [Rotate webhook secret](https://docs.vast.ai/api-reference/notifications/rotate-notification-webhook-secret)
