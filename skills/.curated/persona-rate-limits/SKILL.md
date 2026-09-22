---
name: persona-rate-limits
description: >-
  Analyze and control Persona request rate and product quotas from live headers, Dashboard limits, and durable retry state. Use when scaling or handling 429 responses. Trigger with: "Persona rate limit", "throttle Persona API", "handle Persona 429".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[operation-and-volume]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - persona
  - rate-limits
  - quotas
  - retries
compatibility: 'Requires an authorized Persona environment, current first-party documentation, a reviewed dated API version, and privacy-safe operational evidence.'
---

# Persona Environment Limit and Product Quota Controller

## Overview

Replace invented fixed tables with two current signals: environment request limits and product-specific quotas. Production environments default to 300 requests per minute in current documentation, but Dashboard configuration and response headers govern the running integration.

## Prerequisites

- Endpoint and operation inventory with expected volume
- Current environment limits and product quotas from the Dashboard
- Durable operation, retry, and reconciliation state

## Instructions

### Step 1: Classify work

Separate reads, idempotent POSTs, session operations, reconciliation, and product-consuming verification work. Assign independent worker lanes.

### Step 2: Read live signals

Capture `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`, `Quota-Limit`, `Quota-Remaining`, and `Quota-Reset` where returned. Do not assume every endpoint exposes identical values.

### Step 3: Budget below the boundary

Use token buckets per environment and constrained product. Persona recommends throttling when fewer than 15 percent of requests remain.

### Step 4: Back off on 429

Honor reset or retry guidance. Where no more specific instruction exists, use the documented exponential sequence of 5, 10, 20, and 40 seconds with jitter and a finite budget.

### Step 5: Protect mutations

Use `Idempotency-Key` on POST and persist identical parameters. After timeout or throttle ambiguity, reconcile resource state before retry.

### Step 6: Escalate quota exhaustion

Pause only the affected lane, surface renewal time and business impact, and require approval before changing a paid product or verification policy.

## Authentication

Rate-control workers use the same environment-scoped bearer authentication and dated API version as the guarded request. Telemetry may record header values but never the bearer key or PII payload.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, resume, approve, decline, redact, rotate, revoke, deploy, or otherwise mutate production Persona resources without explicit operator approval.

## Output

- Per-environment and per-product control policy
- Live header, retry, and reconciliation telemetry
- Quota-exhaustion escalation and capacity receipt

Return the environment, resource and event identifiers, API version, template context, source-contract fingerprint, evidence, unresolved risk, rollback state, and final decision without exposing bearer keys, webhook secrets, inquiry session tokens, raw identity documents, or unnecessary PII.

## Examples

At 12 percent request capacity remaining, the controller slows non-urgent reads, preserves webhook ingestion, and queues creates. A 429 enters a bounded 5/10/20/40-second retry schedule while the worker reconciles any POST that may have succeeded.

## Error Handling

| Failure | Response |
| --- | --- |
| Headers disagree with a static value | Trust the current Dashboard and response contract, record drift, and update the reviewed policy. |
| Quota exhausted before rate limit | Pause the product-consuming operation while unrelated reads continue. |
| Repeated 429 after retry budget | Open the circuit, preserve the queue, and escalate rather than looping. |

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
