---
name: palantir-webhooks-events
description: >-
  Choose and implement a supported Foundry event path using OSDK object subscriptions, direct WebSocket subscriptions, monitoring webhooks, or Data Connection webhooks. Use when reacting to object or monitoring changes. Trigger with "Palantir events" or "Foundry subscription".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[object-set-or-monitoring-view]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, events, subscriptions]
---
# Palantir Event and Subscription Integration

## Overview

Start from the event producer and delivery guarantee: real-time Ontology object updates use OSDK or Object Set Watcher WebSocket subscriptions, while monitoring notifications and outbound integrations use their documented webhook surfaces. Never invent a general `ontology.object.created` registration API.

## Prerequisites

- Identify the producer, consumer, object set or monitoring view, supported delivery surface, data sensitivity, latency objective, and recovery behavior.
- Confirm the generated OSDK version or direct WebSocket contract, or the configured Data Connection webhook required by monitoring.
- Read `references/official-docs.md` and verify target-enrollment feature access.
- Prepare a non-production object set or monitoring view and an idempotent consumer.

## Current Contract

- TypeScript OSDK subscriptions require a compatible generated OSDK/client and receive object-set updates through `.subscribe`.
- Direct Object Set Watcher subscriptions use a documented WebSocket endpoint and authenticate with a bearer token encoded in the WebSocket subprotocol format.
- Subscriptions can report an out-of-date state that requires reloading the full object set.
- Monitoring views can route notifications through webhooks configured in Data Connection; that is distinct from Ontology object subscriptions.

## Authentication

Use the generated OSDK token provider or the documented WebSocket bearer subprotocol. For outbound webhooks, use the authentication configured by the supported Data Connection webhook. Never invent or assume a signature header; record the actual configured authentication and secret owner.

## Instructions

1. Classify the event need as Ontology object-set change, monitoring notification, or another documented Foundry integration.

2. Choose TypeScript OSDK subscription, direct WebSocket, or monitoring/Data Connection webhook and document why it matches.

3. Define bounded object filters or monitoring criteria, returned properties/message content, authentication, reconnect/backoff, and cancellation.

4. Implement idempotency and durable reconciliation; on `onOutOfDate`, disconnection, or delivery gap, reload authoritative state.

5. Test create/update/delete or alert cases, duplicate delivery, reconnect, stale state, denied access, secret rotation, and consumer recovery.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

Ontology and data owners approve subscribed objects/properties; security owners approve authentication and outbound destinations; monitoring owners approve notification routing. A subscription does not authorize writeback.

## Output

An event contract with producer, supported surface, filter, payload fields, auth, consumer, delivery/reconnect behavior, idempotency key, reconciliation, tests, observability, and disable procedure.

## Error Handling

| Condition | Response |
|---|---|
| The requested event has no documented surface | Do not invent one; use polling with an approved budget, a supported monitoring route, or ask Palantir Support. |
| The subscription reports out of date | Reload the bounded authoritative object set and reconcile before processing more deltas. |
| WebSocket reconnect loops | Apply bounded backoff, refresh auth as designed, and alert after the retry budget. |
| A webhook auth header is assumed | Stop and inspect the actual Data Connection webhook configuration. |

## Examples

### Example 1

Subscribe to an approved `Equipment` object set with TypeScript OSDK, select only required properties, handle updates and deletion, and reload on `onOutOfDate`.

### Example 2

Route a monitoring-view severity to a preconfigured Data Connection webhook, validate the `Message` input mapping, destination controls, duplicate handling, and disable path.

## Validation

- The chosen surface is explicitly documented for the producer.
- Filters and returned data are least privilege.
- Authentication and secret rotation match the selected surface.
- Duplicates, disconnects, out-of-date state, and reconciliation are tested.
- Consumer failure cannot silently lose authoritative state.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
