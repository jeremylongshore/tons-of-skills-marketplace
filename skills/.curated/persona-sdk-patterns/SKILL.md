---
name: persona-sdk-patterns
description: >-
  Design a typed Persona REST adapter that preserves JSON:API envelopes, request evidence, and compatible additions. Use when building a reusable client. Trigger with: "wrap Persona API", "type Persona responses", "Persona SDK pattern".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[language-and-endpoints]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - persona
  - sdk
  - json-api
  - typing
compatibility: 'Requires an authorized Persona environment, current first-party documentation, a reviewed dated API version, and privacy-safe operational evidence.'
---

# Typed Persona REST Adapter and JSON:API Envelope

## Overview

Keep transport, Persona resource envelopes, and domain decisions separate. The adapter should preserve raw identifiers and metadata, tolerate new resources and fields, and expose explicit mutation evidence rather than flattening every response into a brittle model.

## Prerequisites

- Endpoint inventory and approved API version
- Language runtime with HTTP, JSON, and constant-time comparison support
- Domain boundary defining what may contain PII

## Instructions

### Step 1: Define the transport core

Centralize the API base, bearer header, dated version, timeouts, request IDs, and safe telemetry. Do not retry mutations blindly.

### Step 2: Model JSON:API generically

Represent `data`, `type`, `id`, `attributes`, `relationships`, `included`, `meta`, `links`, and structured errors before adding endpoint-specific views.

### Step 3: Preserve compatible additions

Treat unknown fields, resource types, event types, and array order changes as data to preserve or ignore safely, not parse failures.

### Step 4: Separate command from query

Require an operation ID and `Idempotency-Key` for POST commands. Queries may use bounded retries; commands reconcile observed state after ambiguity.

### Step 5: Normalize evidence, not identity

Return status, request ID, rate and quota headers, resource ID, and a redacted envelope hash. Keep customer attributes behind the domain privacy boundary.

### Step 6: Test with contract fixtures

Cover errors, pagination, unknown fields, multiple verification types, session metadata, throttling, and ambiguous POST outcomes.

## Authentication

Inject the environment-scoped bearer key at the transport boundary and pin `Persona-Version` per request. Callers must never pass raw credentials or select an arbitrary host.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, resume, approve, decline, redact, rotate, revoke, deploy, or otherwise mutate production Persona resources without explicit operator approval.

## Output

- Typed transport and JSON:API envelope interfaces
- Mutation command and read-query contracts
- Compatibility and redaction test matrix

Return the environment, resource and event identifiers, API version, template context, source-contract fingerprint, evidence, unresolved risk, rollback state, and final decision without exposing bearer keys, webhook secrets, inquiry session tokens, raw identity documents, or unnecessary PII.

## Examples

A TypeScript adapter returns `PersonaEnvelope<Inquiry>` plus a redacted request receipt. An unknown relationship is retained in the raw envelope while the domain mapper continues using the fields it understands.

## Error Handling

| Failure | Response |
| --- | --- |
| Unknown type or field | Preserve or ignore it safely and surface a compatibility metric; do not reject a compatible API addition. |
| Timeout after POST | Read the resource or operation evidence before considering a replay with the same parameters. |
| Malformed error envelope | Return transport status and a redacted body hash while protecting PII. |

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
