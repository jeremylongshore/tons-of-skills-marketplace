---
name: persona-webhooks-events
description: >-
  Verify, persist, deduplicate, order, and reconcile Persona webhook events from exact raw bytes. Use when implementing webhook consumers. Trigger with: "handle Persona webhook", "verify Persona-Signature", "dedupe Persona events".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[endpoint-and-event-policy]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - persona
  - webhooks
  - hmac
  - idempotency
compatibility: 'Requires an authorized Persona environment, current first-party documentation, a reviewed dated API version, and privacy-safe operational evidence.'
---

# Authentic and Idempotent Persona Event Intake

## Overview

A webhook is an untrusted delivery until its signature passes. Persona may deliver duplicates or events out of order, so authenticity, durable receipt, idempotency, event-time ordering, and resource reconciliation are distinct steps.

## Prerequisites

- HTTPS endpoint retaining exact raw request bytes
- Persona webhook secret with rotation metadata
- Durable unique event store and reconciliation worker

## Instructions

### Step 1: Capture before parsing

Read the exact raw bytes and `Persona-Signature` header. Enforce size, method, content-type, and timestamp policy before business work.

### Step 2: Parse signature candidates

Extract `t` and every `v1` value. Reject malformed or missing components; retain only redacted diagnostic metadata.

### Step 3: Compute and compare

Compute HMAC-SHA256 with the webhook secret over `t + '.' + rawBody`. Compare against every `v1` candidate in constant time to support rotation.

### Step 4: Acknowledge durable receipt

After authenticity, insert the event ID and raw-body hash under a uniqueness constraint, then acknowledge quickly. Duplicate inserts are successful no-ops.

### Step 5: Process in provider time

Route by event type while tolerating unknown types. Use `data.attributes.created-at`, not arrival order, to guard state transitions.

### Step 6: Reconcile before consequential action

For approval, rejection, payout, or access changes, read the current Persona resource and apply the versioned domain policy.

## Authentication

Webhook authentication uses the endpoint signing secret and the `Persona-Signature` HMAC protocol; it does not use the REST bearer key. Resource reconciliation uses the environment bearer key separately.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, resume, approve, decline, redact, rotate, revoke, deploy, or otherwise mutate production Persona resources without explicit operator approval.

## Output

- Signature-verification contract and test vectors
- Durable event receipt, dedupe, ordering, and routing design
- Reconciliation and business-transition receipt

Return the environment, resource and event identifiers, API version, template context, source-contract fingerprint, evidence, unresolved risk, rollback state, and final decision without exposing bearer keys, webhook secrets, inquiry session tokens, raw identity documents, or unnecessary PII.

## Examples

During rotation a header contains two `v1` candidates. The consumer computes both constant-time comparisons, accepts the matching active secret, stores the event once, and ignores a later duplicate delivery.

## Error Handling

| Failure | Response |
| --- | --- |
| Signature mismatch | Return the configured failure response, record a redacted hash and timestamp, and never enqueue business work. |
| Duplicate event | Acknowledge the already persisted ID without repeating side effects. |
| Older event arrives later | Store it for audit, compare provider creation time and current resource state, and prevent regression. |
| Unknown event type | Preserve and observe it safely; do not crash the intake lane. |

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
