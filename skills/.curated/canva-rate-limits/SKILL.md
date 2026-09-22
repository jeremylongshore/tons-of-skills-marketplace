---
name: canva-rate-limits
description: 'Implement endpoint- and user-scoped Canva throttling with bounded backoff and reconciliation. Use when handling HTTP 429, sizing concurrency, or preventing duplicate asynchronous jobs. Trigger with: "Canva rate limit", "Canva 429", "throttle Canva requests".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[endpoint-and-traffic-profile]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - ratelimit
  - operations
compatibility: 'Requires current endpoint rate metadata, observed response evidence, and an application operation ledger.'
---

# Canva Endpoint Throttling Control

## Overview

Canva limits vary by endpoint and are represented in current endpoint/OpenAPI metadata. Do not invent daily export quotas or assume universal headroom/reset headers.

## Prerequisites

- Normalized endpoint, user/tenant class, traffic profile, and current metadata
- Operation idempotency/reconciliation behavior and local retry budget
- Queue ownership, observability, and abort/rollback thresholds

## Instructions

### Step 1: Load current metadata

Use Read and Grep to identify the exact operation and its current endpoint rate annotation. Keep the contract version with the limiter configuration.

### Step 2: Classify the request

Separate safe reads, async status polls, mutating submissions, token exchange, and public key reads. Never share one undifferentiated global bucket.

### Step 3: Persist mutation identity

Record application operation identity and any returned job ID before considering retry. Reconcile existing state after ambiguous transport failure.

### Step 4: Respond to throttling

Pause the affected endpoint/user queue. Honor documented response instructions when present; otherwise apply bounded exponential backoff with jitter under a deadline.

### Step 5: Control concurrency

Use Write or Edit to enforce admission, concurrency, queue age, retry count, and circuit/abort limits below the current known ceiling and measured application capacity.

### Step 6: Detect drift

Alert on sustained 429s, changed endpoint metadata, queue starvation, or new operation shapes; require review rather than automatically increasing throughput.

### Step 7: Prove recovery

Record contract version, scoped limiter state, observed responses, reconciliation result, and whether traffic returned without duplicates.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

Export submissions and export-status polls use separate controls. After an ambiguous timeout, the service checks the existing job instead of consuming capacity by submitting another export.

## Error Handling

| Failure | Response |
| --- | --- |
| Endpoint metadata is absent | Use a conservative local policy and measure; do not invent a provider limit |
| 429 lacks retry instructions | Apply bounded local backoff and reduce concurrency |
| Queue mixes users or tenants | Partition it before resuming |
| Mutation outcome is ambiguous | Reconcile existing state before retry |

## Resources

- [First-party source notes](references/official-docs.md)
- [API request model](https://www.canva.dev/docs/connect/api-requests-responses/)
- [Latest OpenAPI](https://www.canva.dev/sources/connect/api/latest/api.yml)
