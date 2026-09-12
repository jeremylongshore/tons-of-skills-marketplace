---
name: ideogram-webhooks-events
description: >-
  Verify and reconcile Ideogram async webhooks with Ed25519 signatures, replay controls, deduplication, and polling fallback. Use when implementing or auditing an event receiver. Trigger with "verify an Ideogram webhook", "build Ideogram async callbacks", or "debug duplicate Ideogram events".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<receiver-route> <environment> <replay-window>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, webhooks]
model: inherit
effort: high
compatibility: "Designed for Claude Code; receiver tests should use local signed fixtures"
---
# Ideogram Webhook Verification and Reconciliation

## Overview

Accept Ideogram asynchronous completion only after cryptographic verification and idempotent reconciliation. Use the raw request body, bind all signed headers, acknowledge quickly, and retain polling as a recovery path because delivery is not guaranteed.

## Prerequisites

- A public HTTPS receiver, raw-body access, durable event store, queue, and clock.
- The submitted `generation_id`, destination object policy, and polling reconciler.
- Local Ed25519 fixtures for valid, invalid, stale, duplicate, and rotated-key deliveries.

## Current Contract

Async requests can include a webhook URL and return `generation_id`. Ideogram signs callbacks with Ed25519 and publishes keys at `https://api.ideogram.ai/v1/.well-known/jwks.json`. Signed headers identify generation, user, timestamp, key, and signature. Deliveries may duplicate, retries are limited, and polling remains necessary.

## Authentication

Webhook trust comes from signature verification, not a shared API key in the callback. Normal polling uses server-side `IDEOGRAM_API_KEY` in the `Api-Key` header; never expose it to the receiver request.

## Instructions

1. Capture the raw body bytes and required generation-ID, user-ID, timestamp, key-ID, and signature headers before JSON parsing.
2. Compute SHA-256 over the raw body and construct the signed message as generation ID, newline, user ID, newline, timestamp, newline, then the lowercase body hash.
3. Resolve the key ID from the JWKS cache and verify the lowercase-hex Ed25519 signature.
4. Enforce a bounded timestamp window and bind the callback to a known submitted generation and expected application tenant.
5. Persist a deduplication record keyed by generation and delivery evidence, return `2xx` quickly, and enqueue processing.
6. Validate safety, download approved output, persist it, and transition state idempotently.
7. On verification failure, refresh JWKS once; on missing delivery, append the returned generation ID to `GET /v1/generations/` and poll that resource.

## Tool Discipline

Use Read, Glob, and Grep for receiver, queue, state, and fixtures. Use Write and Edit for approved implementation and tests. Do not expose a receiver, submit paid async work, or replay production events by invocation alone.

## Approval Boundaries

Require approval for public routing, production keys, live submissions, replay-window changes, retained identifiers, and storage or publishing. Reject callbacks that cannot be tied to an authorized application operation.

## Error Handling

- Never verify reserialized JSON; whitespace changes break raw-body integrity.
- Refetch JWKS once on an unknown key or verification failure, then reject.
- Duplicate or late valid delivery is an idempotency case, not authority to create another asset.

## Output

Return receiver route class, signature and replay result, opaque generation ID, duplicate state, acknowledgment latency, downstream terminal and storage state, polling fallback, and cleanup. Exclude headers, bodies, URLs, prompts, and images.

## Examples

- Verify a fixture signed over exact raw bytes, acknowledge, then prove one durable state transition across two deliveries.
- Report `signature=pass; replay=fresh; duplicate=yes; transitions=1; poll_fallback=not-needed`.

## Validation

Test byte mutation, header mutation, stale timestamps, unknown and rotated keys, duplicates, out-of-order state, unsafe output, polling fallback, and object deletion. Confirm receiver logs contain no signed body or content.

## Resources

- [Current first-party evidence map](references/official-docs.md) — use the dated endpoint, webhook, billing, team, and training links as the contract index for this workflow.
- Recheck the endpoint-specific page and current OpenAPI description before relying on an enum, limit, beta feature, or lifecycle claim.
- Record live observations as environment-specific evidence, not as universal vendor guarantees.
