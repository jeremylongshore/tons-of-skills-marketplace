---
name: persona-cost-tuning
description: >-
  Review Persona cost drivers through template policy, duplicate prevention, sandbox use, and measured product quotas. Use when reducing spend without weakening controls. Trigger with: "optimize Persona cost", "Persona usage review", "reduce duplicate inquiries".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[workflow-and-period]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - persona
  - cost
  - verification-policy
  - quotas
compatibility: 'Requires an authorized Persona environment, current first-party documentation, a reviewed dated API version, and privacy-safe operational evidence.'
---

# Persona Verification Policy and Duplicate-Control Review

## Overview

Do not invent price tables or skip required identity evidence. Cost work begins with the business policy and current provider commercial terms, then eliminates accidental duplicate inquiries, unnecessary sessions, polling, and avoidable production testing.

## Prerequisites

- Current contract or authorized Dashboard usage data
- Versioned verification and manual-review policy
- Inquiry, session, retry, template, and product-quota metrics

## Instructions

### Step 1: Establish authority

Record billing period, environment, contract source, template versions, verification products, and finance or compliance owner. Treat public examples as non-binding.

### Step 2: Measure workflow demand

Count unique subjects, inquiries, sessions, verification types, retries, abandoned flows, duplicates, manual reviews, and product-quota consumption.

### Step 3: Find accidental duplication

Join internal operation IDs, account references, inquiry IDs, and idempotency evidence. Quantify creates caused by timeouts, races, and client retries.

### Step 4: Review template policy

Compare each verification type with the approved risk tier and regulatory requirement. Changes to evidence requirements need compliance and product approval.

### Step 5: Shift testing to sandbox

Use forced sandbox pass and fail for development and CI because sandbox performs no real checks and has no usage charges.

### Step 6: Implement and verify

Add subject locks, idempotency, event-driven reconciliation, and observability; compare cost and risk indicators before wider rollout.

## Authentication

Cost analysis uses authorized aggregate Dashboard or billing access and minimally scoped Persona API access. Never export customer PII into a finance worksheet.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, resume, approve, decline, redact, rotate, revoke, deploy, or otherwise mutate production Persona resources without explicit operator approval.

## Output

- Measured cost-driver and duplicate-inquiry inventory
- Policy-preserving optimization proposals with owners
- Before/after usage, risk, approval, and rollback receipt

Return the environment, resource and event identifiers, API version, template context, source-contract fingerprint, evidence, unresolved risk, rollback state, and final decision without exposing bearer keys, webhook secrets, inquiry session tokens, raw identity documents, or unnecessary PII.

## Examples

Analysis finds duplicate inquiries after POST timeouts. The service adds durable idempotency keys and state reconciliation, reducing duplicated work without changing the required government-ID and selfie policy.

## Error Handling

| Failure | Response |
| --- | --- |
| No authoritative pricing source | Report usage drivers and scenarios without asserting dollar savings. |
| Optimization removes required evidence | Reject it until the risk and compliance policy is formally changed. |
| Aggregate export contains PII | Stop distribution, purge the export through the approved process, and rebuild with grouped metrics. |

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
