---
name: persona-core-workflow-a
description: >-
  Operate the account-linked Persona inquiry and session lifecycle from creation through safe resume. Use when implementing a customer verification journey. Trigger with: "create Persona inquiry", "resume Persona inquiry", "link Persona account".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[account-reference-and-template]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - persona
  - inquiries
  - accounts
  - sessions
compatibility: 'Requires an authorized Persona environment, current first-party documentation, a reviewed dated API version, and privacy-safe operational evidence.'
---

# Account-Linked Persona Inquiry and Session Lifecycle

## Overview

Model the inquiry as a durable server-side workflow. Link the customer reference during supported account auto-creation, issue sessions only when a client needs one, and never assume resuming is harmless or unlimited.

## Prerequisites

- Approved inquiry template and account-linkage policy
- Durable mapping from internal subject to Persona account and inquiry IDs
- Session-token delivery and expiration controls

## Instructions

### Step 1: Resolve the subject

Look up the internal subject and existing Persona account or active inquiry. Prevent concurrent duplicate creates with a subject-scoped operation lock.

### Step 2: Create the inquiry

POST with one template selector, `meta.auto-create-account-reference-id` when needed, and a durable idempotency key. Optionally request an initial inquiry session.

### Step 3: Deliver the session safely

Read `meta['session-token']`, bind it to the intended subject and client, redact it from logs, and apply an application-side expiration and single-delivery policy.

### Step 4: Observe lifecycle events

Use verified webhooks as the primary signal and GET reconciliation as a recovery path. Persist Persona event IDs and creation times.

### Step 5: Resume only on demand

For an eligible pending inquiry, call `/inquiries/:id/resume` and read `meta.session-token`. Avoid eager resume because an inquiry has a default maximum of 25 sessions.

### Step 6: Close the domain decision

Map observed inquiry and verification evidence into a separately reviewed business decision. Keep retry, manual review, and terminal states explicit.

## Authentication

Server-side lifecycle calls use the environment bearer key and dated API version. Inquiry session tokens are short-lived client capabilities and must not be treated as API keys or logged.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, resume, approve, decline, redact, rotate, revoke, deploy, or otherwise mutate production Persona resources without explicit operator approval.

## Output

- Subject-to-account-to-inquiry lineage
- Session issuance and resume ledger
- Observed lifecycle and domain-decision receipt

Return the environment, resource and event identifiers, API version, template context, source-contract fingerprint, evidence, unresolved risk, rollback state, and final decision without exposing bearer keys, webhook secrets, inquiry session tokens, raw identity documents, or unnecessary PII.

## Examples

A returning customer with a pending inquiry requests continuation. The service verifies subject ownership, sees no usable active session, resumes once, stores only a token hash and issuance time, and delivers the token to that authenticated client.

## Error Handling

| Failure | Response |
| --- | --- |
| Duplicate active inquiries | Stop creation, reconcile by internal subject and account, and select the authoritative inquiry. |
| Resume rejected | Read current inquiry status and session history; do not loop or create a replacement automatically. |
| Session limit risk | Escalate before the default 25-session ceiling and investigate client churn or repeated resume calls. |

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
