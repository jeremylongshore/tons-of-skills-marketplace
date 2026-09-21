---
name: procore-reference-architecture
description: >-
  Design a governed Procore data connector with explicit tenant routing, durable work queues, endpoint adapters, webhook hydration, reconciliation, and audit receipts. Use when choosing integration boundaries or reviewing a production architecture. Trigger with: "design a Procore connector", "review Procore architecture", "plan Procore data synchronization".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[systems-data-domains-and-freshness-objectives]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - architecture
  - data-connector
compatibility: 'Requires approved system boundaries, Procore app ownership, data classification, and durable queue and state storage.'
---

# Procore Governed Connector Architecture

## Overview

Separate identity, tenant routing, ingestion, hydration, reconciliation, mutation approval, and audit evidence. Procore webhooks improve freshness but REST remains the data source, so the architecture must tolerate duplicates, delays, missed notifications, and partial writes.

## Prerequisites

- Source and destination ownership, data domains, classification, and residency constraints
- Freshness, completeness, recovery, and deletion objectives
- OAuth grant, DMSA permission map, environment matrix, and endpoint inventory

## Instructions

### Step 1: Draw trust boundaries

Identify token service, ingress, queue, workers, state store, outbound adapters, audit sink, and operator interface. Carry company and project context as immutable job attributes.

### Step 2: Separate adapter contracts

Keep endpoint version, request schema, pagination, rate metadata, and errors inside resource adapters. Do not create one fictional global Procore API version.

### Step 3: Design dual ingestion

Accept webhook notifications into a durable queue for freshness. Hydrate current resources through REST and run periodic cursor-based reconciliation for completeness.

### Step 4: Make processing idempotent

Deduplicate events, use origin identifiers or documented sync actions where supported, maintain checkpoints, and reconcile ambiguous mutations before retrying.

### Step 5: Govern writes

Validate scope, render a preview, obtain approval where required, execute once, read after write, and emit a redacted receipt. Keep read and write worker authority separable.

### Step 6: Prove failure behavior

Test token expiry, tenant-routing loss, duplicate and discarded events, rate exhaustion, provider outage, poison records, rollback, and replay from checkpoints.

## Authentication

The token service obtains OAuth 2.0 credentials for the intended user or DMSA boundary and injects Bearer tokens only at dispatch. Every job retains explicit company and project routing without logging tokens.

## Tool Discipline

Use Read and Grep to inspect topology, data contracts, and existing controls. Use Write or Edit only for the approved architecture, adapter contract, test plan, or receipt; no provider mutation is implied by architecture work.

## Output

- Trust-boundary and data-flow design
- Endpoint, queue, checkpoint, reconciliation, and permission contracts
- Failure, rollback, replay, and observability plan

Return decisions, rejected alternatives, assumptions, owners, and measurable acceptance criteria.

## Examples

A webhook receiver queues only event metadata and acknowledges quickly. A tenant-bound worker hydrates the current record through a versioned adapter, deduplicates it, updates downstream state, and advances a checkpoint that a nightly reconciliation can independently verify.

## Error Handling

| Failure | Response |
| --- | --- |
| Company context is absent | Dead-letter the job and fail closed before dispatch. |
| Notification was lost | Reconciliation discovers the changed resource and repairs downstream state. |
| Mutation outcome is ambiguous | Read provider state and compare the intended correlation before retrying. |
| Adapter version is deprecated | Isolate and migrate that resource contract without changing unrelated domains. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Build a data connector app](https://developers.procore.com/documentation/building-data-connection-apps)
- [Webhook reliability](https://developers.procore.com/documentation/webhooks)
- [API usage guidelines](https://developers.procore.com/documentation/api-usage-guidelines)
