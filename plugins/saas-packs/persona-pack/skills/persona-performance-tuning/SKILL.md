---
name: persona-performance-tuning
description: >-
  Improve Persona integration latency and throughput with event-driven processing, bounded reconciliation, and evidence-based measurement. Use when reducing polling or queue lag. Trigger with: "speed up Persona", "reduce inquiry polling", "tune Persona webhooks".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[latency-slo-and-volume]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - persona
  - performance
  - webhooks
  - reconciliation
compatibility: 'Requires an authorized Persona environment, current first-party documentation, a reviewed dated API version, and privacy-safe operational evidence.'
---

# Event-Driven Persona Inquiry Reconciliation

## Overview

Optimize the application around authentic webhook events and bounded GET reconciliation rather than parallel polling or speculative session creation. Measure customer latency, queue lag, rate headroom, and decision freshness separately.

## Prerequisites

- Latency SLO and volume by workflow
- Current traces for API calls, webhook receipt, queueing, and decisions
- Rate and quota header telemetry plus failure budget

## Instructions

### Step 1: Build the latency model

Measure inquiry create, client start, verification progress, provider event creation, delivery, queue delay, reconciliation, and domain decision.

### Step 2: Remove polling from the hot path

Use verified webhooks as the primary notification. Keep bounded polling only for recovery and customer-visible refresh with jitter and stop conditions.

### Step 3: Partition safely

Process unrelated accounts or inquiries concurrently while serializing consequential transitions per subject or inquiry.

### Step 4: Avoid session churn

Create or resume an inquiry session only when a client needs it; track issuance and prevent retries from consuming the default session allowance.

### Step 5: Cache only stable metadata

Cache template and non-sensitive configuration with versioned invalidation. Do not cache bearer credentials, session tokens, or stale identity decisions.

### Step 6: Tune from evidence

Adjust worker count, batch size, timeout, and reconciliation interval while protecting `RateLimit-*`, `Quota-*`, error, and stale-decision thresholds.

## Authentication

Performance work must preserve bearer-key isolation, raw webhook HMAC verification, and session-token confidentiality. Bypassing authentication or reconciliation is not an optimization.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, resume, approve, decline, redact, rotate, revoke, deploy, or otherwise mutate production Persona resources without explicit operator approval.

## Output

- End-to-end latency and queue model
- Polling-removal and concurrency plan
- Before/after SLO, limit headroom, correctness, and rollback receipt

Return the environment, resource and event identifiers, API version, template context, source-contract fingerprint, evidence, unresolved risk, rollback state, and final decision without exposing bearer keys, webhook secrets, inquiry session tokens, raw identity documents, or unnecessary PII.

## Examples

The service replaces five-second polling with verified events and a 90-second reconciliation timer. Median decision latency falls while request volume drops, and per-inquiry serialization prevents stale event transitions.

## Error Handling

| Failure | Response |
| --- | --- |
| Queue lag improves but decisions regress | Roll back worker tuning and inspect per-subject ordering and reconciliation. |
| Rate headroom falls below 15 percent | Throttle background reads and preserve critical intake and reconciliation. |
| Session count grows unexpectedly | Stop eager resume calls and trace client retry behavior. |

## Validation

Verify the result against the linked first-party evidence, the pinned API version, redacted contract fixtures, an expected failure path, and the documented rollback or manual-disposition path. A successful request is not proof of a successful identity decision.

## Resources

- [First-party source notes](references/official-docs.md)
- [API introduction](https://docs.withpersona.com/api-introduction)
- [API quickstart](https://docs.withpersona.com/api-quickstart-tutorial)
- [API keys](https://docs.withpersona.com/api-keys)
- [Rate limits](https://docs.withpersona.com/rate-limiting)
- [Webhook best practices](https://docs.withpersona.com/webhooks-best-practices)
- [Request idempotence](https://docs.withpersona.com/idempotence)
