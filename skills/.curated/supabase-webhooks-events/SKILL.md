---
name: supabase-webhooks-events
description: 'Implement Supabase database webhooks, pg_net async HTTP, LISTEN/NOTIFY,

  and Edge Function event handlers with signature verification.

  Use when setting up database webhooks for INSERT/UPDATE/DELETE events,

  sending HTTP requests from PostgreSQL triggers, handling Realtime

  postgres_changes as an event source, or building event-driven architectures.

  Trigger with phrases like "supabase webhook", "database events",

  "pg_net trigger", "supabase LISTEN NOTIFY", "webhook signature verify",

  "supabase event-driven", "supabase_functions.http_request".

  '
allowed-tools: Write, Bash(supabase:*), Bash(curl:*), Bash(psql:*)
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - supabase
  - webhooks
  - events
  - triggers
  - pg_net
  - realtime
compatibility: Designed for Claude Code
---

# Supabase Webhooks and Database Events

## Overview

Choose Database Webhooks/pg_net for configured outbound HTTP, LISTEN/NOTIFY for
lightweight database notifications, or Realtime Postgres Changes for UI updates.
These mechanisms have different durability, authentication, replay and failure
contracts. This skill's concrete signed receiver illustrates accepted inbox
INGESTION, not complete business processing or exactly-once delivery.

## Prerequisites

- A reviewed producer/receiver contract and intended project identity
- Reviewed migrations, endpoint configuration and secret provisioning
- A durable producer event ID/outbox if reliable signed ingestion is required
- An explicitly authorized deployment workflow; reading this skill deploys nothing

## Authentication

Native Database Webhooks send the HTTP headers you configure. They do not
implicitly generate the custom HMAC protocol below. Do not send a project
service-role key to an arbitrary outbound URL as a generic webhook secret.
Use a receiver-specific credential or the documented intended gateway identity,
kept in an appropriate secret store, with minimal capability and rotation scope.

For the application-owned HMAC example, the sender and receiver BOTH implement
[the exact raw-byte and timestamp contract](references/signature-verification.md).
Missing receiver configuration, invalid signature, stale/future timestamp or
malformed input is rejected before inbox insertion. Timestamp freshness alone is
not durable replay prevention.

The gateway and handler must agree: a JWT-protected Edge Function needs the actual
supported gateway authentication identity; an HMAC-only endpoint requires a
consciously configured dedicated route that permits that sender and enforces HMAC
inside the handler. Do not blindly disable JWT checks on other functions or claim
that HMAC headers satisfy JWT verification. A receiver's server-only database key
is not an outbound sender credential and must never appear in delivery headers.

## Instructions

### Step 1: Select One Delivery Contract

Inventory the event source, authorized endpoint, payload fields, producer identity,
retries, timeout, dead-letter path and protected evidence. Review any trigger SQL
before applying it. A Database Webhook payload (`type`, `table`, `record`,
`old_record`) is not automatically the custom signed inbox envelope. The legacy
[Database Webhook reference](references/database-webhooks.md) describes transport
mechanics; its SQL alone does not provide this custom signature/outbox guarantee.
Do not connect an unsigned trigger to the signed receiver and weaken verification
to make it pass.

### Step 2: Authenticate and Persist an Inbox Record

Use [the bounded receiver and explicit inbox schema](references/edge-function-receivers.md)
with [the matching sender/verifier](references/signature-verification.md). The
producer supplies a unique event ID for each distinct event and retains it across
retries. The receiver authenticates raw bytes before strict JSON/schema validation,
then attempts one unique-key insert. No SELECT-then-side-effect-INSERT sequence and
no row-ID/type-derived deduplication key is used.

202 means accepted into the inbox, with `processingComplete: false`. 409 means the
ID already exists and requires producer-receipt reconciliation, not proof of
completed effects or identical payload. A lost response after commit requires
reconciliation of that SAME ID. Build a separate authorized worker with durable
lease/retry/dead-letter and effect-idempotency semantics before enabling business
actions. No executable business stub is supplied here.

### Step 3: Treat Notifications as Hints, Not Durable Work Completion

LISTEN/NOTIFY is not a persistent queue. Its payload size has a strict byte limit;
oversized payloads fail rather than being safely truncated. Send minimal IDs and
re-read authorized state. Realtime subscriptions similarly need correct user/RLS
and publication setup plus reconciliation after reconnect. Do not log changed rows
or infer guaranteed event recovery from a successful subscription.

See [notification and Realtime mechanics](references/listen-notify-realtime.md),
reviewing authentication, lifecycle cleanup and evidence boundaries for the actual
application before adopting any example.

## Output

- Explicit transport and authentication contracts, with native/custom boundaries
- Unique producer event IDs and durable accepted-inbox receipts
- Separate worker/retry/reconciliation requirements and unresolved processing state
- Operational evidence without payloads, tokens or secret headers

## Error Handling

| Observation                | Required check                                                                           |
| -------------------------- | ---------------------------------------------------------------------------------------- |
| HTTP 401/403               | Match actual gateway and handler authentication; never bypass verification to resolve it |
| Missing HMAC configuration | Fail closed; do not insert or acknowledge acceptance                                     |
| Duplicate event ID         | Reconcile durable producer/inbox receipts; do not invent a new ID for the retry          |
| Inbox error/timeout        | No completed-effects claim; reconcile possible commit before retry                       |
| Realtime silence           | Check identity, policies, publication, connectivity and reconciliation                   |
| NOTIFY oversize            | Reduce to IDs; no truncation guarantee                                                   |

## Examples

- [Signed protocol and request builder](references/signature-verification.md):
  explicit application-owned headers/raw bytes, not a native signing claim.
- [Inbox receiver](references/edge-function-receivers.md): bounded validation and
  checked unique insertion, no business completion acknowledgment.

## Resources

- [Database Webhooks](https://supabase.com/docs/guides/database/webhooks)
- [pg_net](https://supabase.com/docs/guides/database/extensions/pg_net)
- [Securing Edge Functions](https://supabase.com/docs/guides/functions/auth)
- [Realtime Postgres Changes](https://supabase.com/docs/guides/realtime/postgres-changes)
- [PostgreSQL NOTIFY](https://www.postgresql.org/docs/current/sql-notify.html)

## Next Steps

Review worker authorization, durable delivery/processing receipts, replay horizons
and failure recovery before enabling side effects or claiming production readiness.
