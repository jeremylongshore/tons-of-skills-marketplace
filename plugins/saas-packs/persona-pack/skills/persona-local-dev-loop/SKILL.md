---
name: persona-local-dev-loop
description: >-
  Run a deterministic local Persona sandbox loop with synthetic inquiries, raw webhook fixtures, and replay checks. Use when developing without production PII. Trigger with: "develop Persona locally", "test Persona webhook", "mock Persona flow".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[fixture-scenario]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - persona
  - local-development
  - sandbox
  - webhooks
compatibility: 'Requires an authorized Persona environment, current first-party documentation, a reviewed dated API version, and privacy-safe operational evidence.'
---

# Deterministic Persona Sandbox and Webhook Loop

## Overview

Build the local loop around Persona sandbox behavior and captured contract fixtures, not around calls to production. Sandbox performs no real verification, supports forced pass or fail paths, and incurs no usage charges.

## Prerequisites

- Sandbox-only API key and template
- HTTPS-capable webhook tunnel or local fixture runner
- Synthetic identities and a secret-safe fixture directory

## Instructions

### Step 1: Declare the scenario

Name the template, forced outcome, inquiry state, expected event type, API version, and cleanup disposition.

### Step 2: Create with an operation key

Create a sandbox inquiry using a unique `Idempotency-Key`. Persist IDs separately from synthetic payloads.

### Step 3: Exercise the client path

Use the supported sandbox flow to force pass or fail. Do not encode sandbox-only controls into production request code.

### Step 4: Capture raw webhook bytes

Save headers and raw body before parsing, redact PII, and preserve duplicate deliveries and deliberately reordered fixtures.

### Step 5: Replay deterministically

Verify HMAC against raw bytes, deduplicate by event ID, order business processing by `data.attributes.created-at`, and assert the terminal local state.

### Step 6: Reset without hiding drift

Delete only generated local artifacts through the project’s approved cleanup path; retain the contract fingerprint and test receipt.

## Authentication

Use a sandbox bearer key for REST requests and a separate sandbox webhook secret for HMAC verification. Never expose either value in a tunnel URL, fixture, console log, or committed `.env` file.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, resume, approve, decline, redact, rotate, revoke, deploy, or otherwise mutate production Persona resources without explicit operator approval.

## Output

- Named sandbox scenario and synthetic inquiry receipt
- Redacted raw webhook fixture set
- Replay, duplicate, ordering, and terminal-state assertions

Return the environment, resource and event identifiers, API version, template context, source-contract fingerprint, evidence, unresolved risk, rollback state, and final decision without exposing bearer keys, webhook secrets, inquiry session tokens, raw identity documents, or unnecessary PII.

## Examples

The `government-id-fail` scenario creates a sandbox inquiry, forces failure, captures two deliveries of the same event, replays them out of order, and proves exactly one transition to the expected failed state.

## Error Handling

| Failure | Response |
| --- | --- |
| Tunnel receives parsed JSON only | Disable body transformation and retain the exact raw bytes before JSON parsing. |
| Fixture signature fails after editing | Regenerate the signature from the edited timestamp and raw body; never weaken verification. |
| Sandbox and production settings diverge | Record the drift and stop promotion until templates, events, and API version are reviewed. |

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
