---
name: persona-debug-bundle
description: >-
  Assemble a minimal, verifiable Persona diagnostic bundle without exporting secrets or identity payloads. Use when escalating an incident. Trigger with: "collect Persona debug bundle", "escalate Persona issue", "Persona support evidence".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[incident-id-and-window]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - persona
  - diagnostics
  - support
  - privacy
compatibility: 'Requires an authorized Persona environment, current first-party documentation, a reviewed dated API version, and privacy-safe operational evidence.'
---

# Redacted Persona Diagnostic Manifest

## Overview

A useful Persona escalation bundle proves environment, request contract, lifecycle, and event handling while excluding API keys, session tokens, webhook secrets, raw identity documents, and unneeded customer attributes.

## Prerequisites

- Incident ID, UTC window, affected environment, and authorized investigator
- Known inquiry, account, verification, request, or event identifiers
- Approved redaction and secure-transfer policy

## Instructions

### Step 1: Declare scope

Record incident owner, start and end time, affected service, environment, symptom, and collection authorization.

### Step 2: Collect contract evidence

Capture canonical endpoint, method, API version, status, request ID, safe response headers, deployment SHA, and template IDs.

### Step 3: Collect lifecycle evidence

Record only resource IDs, types, statuses, and timestamps needed to reconstruct inquiry and verification transitions.

### Step 4: Collect webhook evidence

Include endpoint ID, event ID and type, delivery time, signature-verification outcome, dedupe result, and raw-body hash—not the secret or full payload.

### Step 5: Build the redaction manifest

List every omitted or transformed field, token, document, image, address, birth date, and customer attribute. Scan the bundle before export.

### Step 6: Seal and transfer

Hash each artifact and the manifest, apply least-privilege access and retention, and record recipient, transfer channel, and deletion date.

## Authentication

Use authorized read-only access where possible. Never place bearer keys, `Persona-Signature` secrets, inquiry session tokens, or signed URLs in the bundle.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, resume, approve, decline, redact, rotate, revoke, deploy, or otherwise mutate production Persona resources without explicit operator approval.

## Output

- Redaction manifest and artifact index
- Chronological request, resource, and webhook evidence
- Hashes, custody, retention, and escalation receipt

Return the environment, resource and event identifiers, API version, template context, source-contract fingerprint, evidence, unresolved risk, rollback state, and final decision without exposing bearer keys, webhook secrets, inquiry session tokens, raw identity documents, or unnecessary PII.

## Examples

A bundle contains a deployment SHA, endpoint and API version, inquiry ID, three status timestamps, two event IDs, signature verdicts, request IDs, and artifact hashes. It contains no names, images, documents, tokens, or raw bodies.

## Error Handling

| Failure | Response |
| --- | --- |
| Bundle contains credential-like text | Quarantine it, rotate any exposed credential, and rebuild from source evidence. |
| Timeline cannot be reconciled | Add provider creation timestamps and delivery attempts rather than copying full payloads. |
| Support requests raw PII | Use the approved secure support process and obtain explicit authorization; do not attach it casually. |

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
