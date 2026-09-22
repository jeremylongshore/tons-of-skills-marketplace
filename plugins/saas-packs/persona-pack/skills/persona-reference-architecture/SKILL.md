---
name: persona-reference-architecture
description: >-
  Design an account-linked KYC control plane around Persona with explicit trust, data, event, and decision boundaries. Use when conducting an architecture review. Trigger with: "architect Persona integration", "Persona KYC design", "design identity workflow".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[system-context-and-risk-tier]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - persona
  - architecture
  - kyc
  - control-plane
compatibility: 'Requires an authorized Persona environment, current first-party documentation, a reviewed dated API version, and privacy-safe operational evidence.'
---

# Account-Linked KYC Control Plane with Persona

## Overview

Put Persona behind a server-side identity orchestration boundary. The application owns subject identity, operation idempotency, policy and decisions; Persona owns inquiry and verification resources; authenticated events plus reconciliation connect the two.

## Prerequisites

- System context, data classification, and threat model
- Business and regulatory decision policy
- Availability, latency, retention, residency, and recovery requirements

## Instructions

### Step 1: Draw trust boundaries

Separate client, application API, orchestration service, secret store, Persona REST API, embedded inquiry flow, webhook edge, durable queue, decision engine, and reviewer console.

### Step 2: Define authoritative identifiers

Map internal subject to Persona account and inquiry IDs. Store operation IDs and event IDs under uniqueness constraints; do not make PII the join key.

### Step 3: Design commands and sessions

Create inquiries with durable idempotency and supported account-auto-create metadata. Issue or resume sessions only through authenticated subject ownership.

### Step 4: Design event intake

Terminate HTTPS, retain raw bytes, verify timestamped HMAC, persist before acknowledgement, deduplicate, order by provider creation time, and tolerate unknown event types.

### Step 5: Separate evidence from decision

Normalize verification resources conservatively, then apply a versioned internal policy with explicit review and appeal paths.

### Step 6: Engineer recovery and privacy

Use durable queues, GET reconciliation, bounded retries, environment and quota controls, data minimization, retention, irreversible-redaction governance, and tested rollback.

## Authentication

The server-side REST boundary owns environment bearer keys; the webhook edge owns signing secrets; the client receives only its inquiry session token. No credential crosses those roles.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, resume, approve, decline, redact, rotate, revoke, deploy, or otherwise mutate production Persona resources without explicit operator approval.

## Output

- Trust and data-flow architecture
- Identifier, command, event, evidence, and decision contracts
- Failure, security, privacy, capacity, rollback, and audit controls

Return the environment, resource and event identifiers, API version, template context, source-contract fingerprint, evidence, unresolved risk, rollback state, and final decision without exposing bearer keys, webhook secrets, inquiry session tokens, raw identity documents, or unnecessary PII.

## Examples

A client asks to resume. The application authenticates the subject, the orchestrator resolves the existing account-linked inquiry, issues one session, and later accepts a signed event into a durable queue before the decision engine reconciles current resources.

## Error Handling

| Failure | Response |
| --- | --- |
| Client can call Persona REST with server key | Redesign the boundary; server bearer credentials must not reach the client. |
| Event delivery directly approves access | Insert durable receipt, reconciliation, and versioned policy evaluation. |
| No manual path during provider outage | Add a risk-approved degraded state and recovery queue before production. |

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
