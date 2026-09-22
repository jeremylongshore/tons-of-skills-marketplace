---
name: runway-webhooks-events
description: >-
  Convert authoritative Runway task polling into durable internal events or signed customer callbacks without claiming native provider webhooks. Use when downstream systems need completion notifications. Trigger with: "Runway task events", "Runway completion webhook", "notify when Runway finishes".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[consumer-and-delivery-policy]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - runway
  - events
  - webhooks
  - polling
compatibility: 'Requires server-side Runway Dev access, current first-party documentation, an approved credit budget, and controlled media storage.'
---

# Runway Polling-to-Event Relay

## Overview

The documented Runway generation surface exposes task retrieval and cancellation, not a native generation-completion webhook endpoint. Build notifications by reconciling provider task state into an internal outbox, then deliver idempotent internal events or your own signed customer webhook.

## Prerequisites

- Durable operations, provider task IDs, and legal state transitions
- A bounded polling scheduler and transactional outbox
- Consumer authentication, signing, retry, and replay policies

## Instructions

### Step 1: State the authority boundary

Document that Runway is polled via `GET /v1/tasks/<task-id>`. Do not configure a fictional provider webhook secret or tell consumers that a callback originated from Runway.

### Step 2: Reconcile provider state

Retrieve due nonterminal tasks at five-second-or-longer jittered intervals with backoff. Treat `THROTTLED` as queued and accept only legal forward transitions to `SUCCEEDED`, `FAILED`, or `CANCELLED`.

### Step 3: Write state and outbox atomically

Persist the newly observed state, provider evidence hash, and one outbox record in the same transaction. Use a uniqueness key such as operation ID plus state version so restarts cannot duplicate logical events.

### Step 4: Shape the internal event

Emit internal operation ID, provider task ID, terminal state, timestamps, model or router metadata, stored-asset ID, and redacted failure class. Never emit bearer keys, prompt/media bodies, or signed provider URLs.

### Step 5: Deliver your callback

For customer webhooks, sign exact raw bytes with your service's secret, include timestamp and event ID, retry with a bound, and expose replay and verification guidance. This is your protocol, not Runway's.

### Step 6: Reconcile delivery

Track attempts, acknowledgements, dead letters, consumer idempotency, and asset authorization. A callback failure must not trigger a new Runway generation.

## Authentication

Provider polling uses the server-side Runway bearer secret and version header. Internal buses use workload identity; customer callbacks use a separate service-owned signing secret and never reuse the Runway key.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, lockfiles, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, cancel, delete, retry, deploy, rotate, revoke, publish, or otherwise mutate production Runway resources without explicit operator approval.

## Output

- Explicit provider-polling and internal-event architecture
- Transactional state/outbox and idempotency contract
- Signed callback schema, retry policy, and delivery receipt

Return the environment, organization alias, operation and task identifiers, API and SDK versions, model or router policy, source-contract fingerprint, task-state evidence, credit boundary, output disposition, unresolved risk, rollback state, and final decision without exposing API secrets, prompt or media contents, or temporary signed URLs.

## Examples

A reconciler observes task `SUCCEEDED`, copies the output, commits state plus one outbox row, and crashes. On restart, the outbox publishes the same event ID once logically; the customer verifies the service signature and deduplicates it.

## Error Handling

| Failure | Response |
| --- | --- |
| Team assumes Runway sends generation webhooks | Correct the design to documented task retrieval unless a new first-party endpoint is verified. |
| Poller emits duplicate terminal events | Enforce the state-version uniqueness key and consumer idempotency. |
| Customer callback fails repeatedly | Dead-letter it after the bound; never resubmit the provider generation. |

## Validation

Test every provider state transition, repeated observations, crashes around the transaction, duplicate publication, signature verification, replay-window rejection, bounded delivery retry, and confirmation that events contain owned asset IDs rather than provider URLs.

## Resources

- [First-party source notes](references/official-docs.md)
- [Runway agent context](https://docs.dev.runwayml.com/ai-context.md)
- [API reference](https://docs.dev.runwayml.com/api.md)
- [Models](https://docs.dev.runwayml.com/guides/models.md)
- [Usage tiers](https://docs.dev.runwayml.com/usage/tiers.md)
- [Pricing](https://docs.dev.runwayml.com/guides/pricing.md)
- [Production checklist](https://docs.dev.runwayml.com/guides/go-live.md)
