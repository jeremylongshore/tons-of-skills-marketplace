---
name: creating-webhook-handlers
description: 'Create webhook endpoints with signature verification, retry logic, and
  payload validation.

  Use when receiving and processing webhook events.

  Trigger with phrases like "create webhook", "handle webhook events", or "setup webhook
  handler".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:webhook-*)
version: 1.26.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- webhooks
- webhook-handlers
compatibility: Designed for Claude Code
---
# Creating Webhook Handlers

## Overview

Create secure webhook receiver endpoints with HMAC signature verification, idempotent event processing, and automatic retry handling. Support ingestion from providers like Stripe, GitHub, Twilio, and Slack with provider-specific signature validation schemes and payload parsing.

## Prerequisites

- Web framework with raw body access (Express with `express.raw()`, FastAPI with `Request.body()`)
- Webhook provider credentials: signing secret or shared secret key
- Persistent storage for idempotency tracking (Redis or database table for processed event IDs)
- Queue system for async processing (optional: Bull, Celery, SQS)
- ngrok or similar tunnel for local development testing

## Instructions

1. Examine existing route definitions and middleware using Grep and Read to identify where webhook endpoints integrate into the application.
2. Create a dedicated webhook route (e.g., `POST /webhooks/:provider`) that captures the raw request body before any JSON parsing middleware runs.
3. Implement HMAC-SHA256 signature verification by computing `HMAC(raw_body, signing_secret)` and comparing against the provider's signature header (`X-Hub-Signature-256`, `Stripe-Signature`, `X-Twilio-Signature`).
4. Add idempotency protection by storing processed event IDs (e.g., `evt_xxx`) in Redis or a database table, rejecting duplicates with 200 OK to prevent provider retries.
5. Parse the event type from the payload (`event.type`, `action`, `EventType`) and route to the appropriate handler function using a dispatch map.
6. Respond with 200 OK immediately, then enqueue the event payload for asynchronous processing to avoid webhook timeout failures.
7. Implement dead-letter handling for events that fail processing after maximum retry attempts, logging the full payload for manual inspection.
8. Write tests that replay recorded webhook payloads with valid and tampered signatures to verify acceptance and rejection behavior.

See `${CLAUDE_SKILL_DIR}/references/implementation.md` for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/src/webhooks/receiver.js` - Webhook endpoint with signature verification
- `${CLAUDE_SKILL_DIR}/src/webhooks/handlers/` - Per-event-type handler functions
- `${CLAUDE_SKILL_DIR}/src/webhooks/verify.js` - HMAC signature verification utilities
- `${CLAUDE_SKILL_DIR}/src/webhooks/idempotency.js` - Duplicate event detection logic
- `${CLAUDE_SKILL_DIR}/src/queues/webhook-processor.js` - Async event processing queue worker
- `${CLAUDE_SKILL_DIR}/tests/webhooks/` - Replay tests with recorded payloads

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Signature Mismatch | HMAC verification failed against provider signature | Log the expected vs. received signature (redacted); verify signing secret rotation status |
| 400 Malformed Payload | Raw body is not valid JSON or missing required fields | Return 400 so provider marks delivery as failed; log raw body for debugging |
| 200 OK (duplicate) | Event ID already processed; idempotency guard triggered | Return 200 to prevent provider retry loops; log duplicate detection for monitoring |
| 504 Gateway Timeout | Synchronous processing exceeded provider timeout (typically 5-30s) | Move processing to async queue; respond 200 immediately upon signature verification |
| 500 Handler Exception | Business logic threw unhandled error during processing | Catch at dispatch layer; log full error with event payload; allow provider to retry |

Refer to `${CLAUDE_SKILL_DIR}/references/errors.md` for comprehensive error patterns.

## Examples

**Stripe payment webhook**: Verify `Stripe-Signature` header using `stripe.webhooks.constructEvent()`, then dispatch `payment_intent.succeeded` to fulfill orders and `charge.refunded` to process refund credits.

**GitHub push webhook**: Validate `X-Hub-Signature-256`, parse `push` events, extract commit list, and trigger CI/CD pipeline via queue message.

**Multi-provider router**: Single `/webhooks/:provider` endpoint that loads provider-specific signature verifier and event schema from a registry, supporting Stripe, GitHub, Twilio, and custom providers.

See `${CLAUDE_SKILL_DIR}/references/examples.md` for additional examples.

## Resources

- Stripe Webhook Signatures: https://stripe.com/docs/webhooks/signatures
- GitHub Webhook Events: https://docs.github.com/en/webhooks
- RFC 2104 HMAC specification for signature computation
- OWASP Webhook Security best practices
