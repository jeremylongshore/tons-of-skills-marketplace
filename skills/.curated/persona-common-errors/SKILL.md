---
name: persona-common-errors
description: >-
  Triage Persona authentication, JSON:API, inquiry, session, webhook, and throttle failures with redacted evidence. Use when an integration is failing. Trigger with: "debug Persona error", "Persona 401", "Persona inquiry failed".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[request-id-or-inquiry-id]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - persona
  - troubleshooting
  - errors
  - inquiries
compatibility: 'Requires an authorized Persona environment, current first-party documentation, a reviewed dated API version, and privacy-safe operational evidence.'
---

# Persona API and Inquiry Failure Triage

## Overview

Diagnose from the outer boundary inward: environment and credentials, request contract, resource lifecycle, session state, webhook authenticity, then provider limits. Preserve the original status and request evidence while keeping identity data out of logs.

## Prerequisites

- Timestamp, environment, endpoint, status, and provider request identifier
- Redacted request fingerprint and relevant inquiry or event ID
- Access to current Dashboard configuration and application logs

## Instructions

### Step 1: Freeze the evidence

Record UTC time, method, canonical host and path, API version, status, request ID, idempotency key hash, and response-body hash.

### Step 2: Check environment and auth

Confirm `api.withpersona.com`, the target environment, key state, permissions, and explicit version. A 401 is not fixed by printing or widening the key.

### Step 3: Validate the request envelope

Check JSON:API shape, template selector, content headers, account auto-create metadata, and replay parameters.

### Step 4: Reconcile lifecycle state

Read the inquiry before retrying a create, resume, or transition. Distinguish pending, terminal, redacted, and unavailable resources.

### Step 5: Verify event intake

Use raw bytes, timestamp-plus-dot-plus-body HMAC, all `v1` candidates, constant-time compare, event-ID dedupe, and creation-time ordering.

### Step 6: Respect limit signals

Read live `RateLimit-*` and `Quota-*` headers and Dashboard product quotas. On 429, reduce the responsible lane and use bounded backoff.

## Authentication

Authenticate REST diagnostics with the correct environment bearer key and webhook diagnostics with the endpoint’s signing secret. Redact both before creating a ticket or debug bundle.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, resume, approve, decline, redact, rotate, revoke, deploy, or otherwise mutate production Persona resources without explicit operator approval.

## Output

- Ranked root-cause hypothesis with evidence
- Safe retry, reconciliation, or manual-review action
- Redacted escalation packet and unresolved risks

Return the environment, resource and event identifiers, API version, template context, source-contract fingerprint, evidence, unresolved risk, rollback state, and final decision without exposing bearer keys, webhook secrets, inquiry session tokens, raw identity documents, or unnecessary PII.

## Examples

A create call times out and its replay returns an unexpected response. The operator compares the stored idempotency key and request fingerprint, queries for the resulting inquiry, and avoids issuing a second customer workflow.

## Error Handling

| Failure | Response |
| --- | --- |
| 401 or 403 | Verify host, environment, key state, permission, and version without exposing the bearer value. |
| 400 or 422 | Inspect the JSON:API error pointers and compare the request to the current endpoint contract. |
| 404 inquiry | Check environment and ID lineage; a redacted or wrong-tenant resource must not trigger blind recreation. |
| 429 | Honor current headers, apply 5/10/20/40-second bounded delay where appropriate, and reconcile before mutation replay. |

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
