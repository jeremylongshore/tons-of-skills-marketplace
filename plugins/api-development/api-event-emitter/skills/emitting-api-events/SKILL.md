---
name: emitting-api-events
description: 'Build event-driven APIs with webhooks, Server-Sent Events, and real-time
  notifications.

  Use when building event-driven API architectures.

  Trigger with phrases like "add webhooks", "implement events", or "create event-driven
  API".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:events-*)
version: 1.25.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- webhooks
- emitting-api
compatibility: Designed for Claude Code
---
# Emitting API Events

## Overview

Build event-driven API architectures using outbound webhooks, Server-Sent Events (SSE), and message broker integration. Implement event emission from API mutations, event schema registry, subscriber management, delivery guarantees with retry logic, and event sourcing patterns for maintaining a complete audit log of API state changes.

## Prerequisites

- Message broker: Redis Pub/Sub, RabbitMQ, Apache Kafka, or AWS SNS/SQS
- Persistent storage for event log and subscriber registrations (PostgreSQL, MongoDB)
- Webhook delivery infrastructure with retry queue (Bull, Celery, or managed service)
- Event schema registry for versioned event type definitions
- SSE-capable web framework for real-time event streaming to browser clients

## Instructions

1. Identify event-producing operations using Grep and Read, cataloging every API mutation (POST, PUT, PATCH, DELETE) that should emit events, with event type names following `resource.action` convention (e.g., `order.created`, `user.updated`).
2. Define event schemas for each event type with versioning: include `eventId` (UUID), `eventType`, `version`, `timestamp` (ISO 8601), `source` (service identifier), and `data` (type-specific payload).
3. Implement the event emitter service that publishes events to the message broker after successful API mutations, using the transactional outbox pattern to ensure events are not lost on application crash.
4. Build a webhook subscription management API: `POST /webhooks` (subscribe), `GET /webhooks` (list), `DELETE /webhooks/:id` (unsubscribe), with URL validation, event type filtering, and signing secret generation.
5. Implement webhook delivery with HMAC-SHA256 signed payloads, configurable retry policy (exponential backoff: 1min, 5min, 30min, 2hr, 24hr), and automatic subscription deactivation after consecutive failures.
6. Add Server-Sent Events endpoint (`GET /events/stream`) for real-time event delivery to browser clients, with `Last-Event-ID` support for reconnection and missed event replay.
7. Create a dead-letter queue for events that exhaust all delivery retry attempts, with alerting and manual replay capability.
8. Write integration tests covering event emission, webhook delivery with signature verification, SSE stream connection with reconnection, and dead-letter queue behavior.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/src/events/emitter.js` - Event emission service with outbox pattern
- `${CLAUDE_SKILL_DIR}/src/events/schemas/` - Versioned event type schema definitions
- `${CLAUDE_SKILL_DIR}/src/events/webhooks/` - Webhook delivery, signing, and retry logic
- `${CLAUDE_SKILL_DIR}/src/events/sse.js` - Server-Sent Events streaming endpoint
- `${CLAUDE_SKILL_DIR}/src/routes/webhooks.js` - Webhook subscription management API
- `${CLAUDE_SKILL_DIR}/src/events/dead-letter.js` - Dead-letter queue handler with replay
- `${CLAUDE_SKILL_DIR}/tests/events/` - Event emission and delivery integration tests

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Event lost on crash | Application crashes between database commit and event publish | Use transactional outbox pattern: write event to outbox table in same transaction, poll and publish separately |
| Webhook delivery failure | Subscriber endpoint unreachable or returns non-2xx | Retry with exponential backoff; deactivate subscription after 5 consecutive failures; notify subscriber admin |
| Event ordering violation | Concurrent mutations publish events out of order | Use partition keys (resource ID) for ordered delivery within a partition; accept out-of-order across partitions |
| SSE connection memory leak | Server accumulates stale SSE connections without cleanup | Implement heartbeat comments (`:keepalive\n\n`) every 15 seconds; detect and close dead connections |
| Schema version mismatch | Consumer expects v1 event format but receives v2 | Include `version` field in event envelope; support simultaneous v1/v2 delivery; deprecate old versions with notice |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**Order lifecycle events**: Emit `order.created`, `order.payment_received`, `order.shipped`, and `order.delivered` events with order details, enabling downstream services (warehouse, email, analytics) to react asynchronously.

**SSE live notifications**: Browser client connects to `GET /events/stream?types=message.received,order.updated` and receives real-time event updates with automatic reconnection and `Last-Event-ID` replay on network interruption.

**Transactional outbox**: Write the event record to an `outbox` table within the same database transaction as the API mutation, then poll the outbox table every 100ms to publish events to Kafka, ensuring at-least-once delivery.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- CloudEvents specification: https://cloudevents.io/
- Server-Sent Events (MDN): https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
- Transactional outbox pattern: Microservices.io
- Webhook best practices: Standard Webhooks specification
