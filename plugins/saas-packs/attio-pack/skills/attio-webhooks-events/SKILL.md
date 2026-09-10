---
name: attio-webhooks-events
description: >-
  Build and operate an Attio webhook receiver with raw-body HMAC verification, fast acknowledgement, durable queues, idempotent processing, retry awareness, and reconciliation. Use when implementing or repairing Attio event delivery. Trigger with "Attio webhooks", "Attio events", or "verify Attio signature".
argument-hint: "[repository-path] [receiver-route]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- attio
- webhooks
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# Attio Webhook Receiver

## Overview

This skill implements the complete event-delivery boundary: authenticate the exact payload, acknowledge within Attio's delivery window, process at least once safely, and reconcile missed or delayed effects.

## Prerequisites

- Public HTTPS receiver and approved webhook secret storage
- Required event types and downstream ownership
- Durable queue and idempotency store
- Replay, dead-letter, and reconciliation procedures

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect raw-body middleware, route handling, queues, and deduplication. Use `WebFetch` only for current official Attio webhook documentation. Use `Write` or `Edit` after the event contract and failure policy are confirmed.

## Current Contract

- Read `Attio-Signature`; legacy deliveries may also expose `X-Attio-Signature`.
- Compute SHA-256 HMAC over the exact raw UTF-8 request body using the webhook secret and compare hexadecimal signatures safely.
- Return a 2xx quickly after validation and durable acceptance; Attio documents a 5-second timeout.
- Delivery is at least once. Use `Idempotency-Key` for deduplication.
- Attio documents up to 10 retries over roughly three days and a delivery limit of 25 requests per second per target URL; reverify before rollout.

## Authentication

Store the webhook secret server-side. Verify the signature before JSON parsing, logging, queueing, or any state change, and support controlled secret rotation.

## Instructions

1. Capture the raw request bytes before body-parsing middleware transforms them.
2. Read the supported signature header, decode the expected hex, and reject malformed or unequal-length values.
3. Compute raw-body HMAC and use a timing-safe equal-length comparison.
4. Validate the event envelope and reserve `Idempotency-Key` transactionally.
5. Persist the event to a durable queue, then return 2xx within the timeout.
6. Process idempotently with bounded concurrency, explicit dead-letter handling, and redacted telemetry.
7. Test valid, invalid, duplicate, reordered, delayed, burst, queue-failure, and secret-rotation cases.
8. Reconcile authoritative Attio state so a missed event cannot create permanent drift.

## Approval Boundaries

Do not create production subscriptions, rotate secrets, replay events, or mutate downstream customer state without the responsible owner and rollback controls.

## Output

Return the subscription scope, signature evidence, acknowledgement path, idempotency design, queue behavior, failure tests, reconciliation procedure, and owners.

## Error Handling

| Condition | Response |
|---|---|
| Signature is absent or invalid | Reject without parsing or side effects. |
| Idempotency key already committed | Return success without repeating work. |
| Durable queue is unavailable | Return failure so delivery can be retried. |
| Handler exceeds the timeout | Move work behind the queue and acknowledge earlier. |

## Examples

Input:

```text
route=/webhooks/attio; events=record updates; queue=durable
```

Expected handoff:

```text
hmac=raw-body verified; ack=under-timeout; dedupe=transactional; replay=tested
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Webhooks](https://docs.attio.com/rest-api/guides/webhooks)
- [REST API overview](https://docs.attio.com/rest-api/overview)
