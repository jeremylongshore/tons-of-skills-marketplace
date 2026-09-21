---
name: persona-hello-world
description: >-
  Create and inspect one replay-safe Persona sandbox inquiry without implying a completed verification. Use when proving a new integration path. Trigger with: "test Persona inquiry", "Persona hello world", "smoke test Persona sandbox".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[sandbox-template-id]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - persona
  - sandbox
  - inquiries
  - smoke-test
compatibility: 'Requires an authorized Persona environment, current first-party documentation, a reviewed dated API version, and privacy-safe operational evidence.'
---

# Persona Sandbox Inquiry Smoke Test

## Overview

Prove the minimum create-and-read path in sandbox while keeping identity verification, account linkage, and session issuance explicit. A successful API response proves transport and contract compatibility, not that a person passed verification.

## Prerequisites

- A sandbox API key and a reviewed dated API version
- An enabled sandbox inquiry template ID
- Synthetic test identity data and a durable unique operation ID

## Instructions

### Step 1: Choose the create contract

Use exactly one of `inquiry-template-id`, `inquiry-template-version-id`, or the supported template selector. Prefer the stable template ID unless a controlled test intentionally pins a version.

### Step 2: Create replay-safe intent

Generate an `Idempotency-Key` from the operation ID, not a person or reference ID. Persist the request fingerprint before sending the POST.

### Step 3: Link the account deliberately

When auto-creating an account, use `meta.auto-create-account-reference-id`; do not revive deprecated request `reference-id` guidance. Use `meta.auto-create-inquiry-session` only when the client needs an immediate session.

### Step 4: Inspect the JSON:API result

Verify `data.type`, inquiry ID, status, template relationship, and optional `meta['session-token']`. Treat new fields and types as compatible additions.

### Step 5: Read and dispose

GET the inquiry, compare its ID and status, then retain a redacted receipt. Never claim pass, fail, or completion unless the observed inquiry and verification states support it.

## Authentication

Use the sandbox bearer API key against `https://api.withpersona.com/api/v1` with the explicitly reviewed `Persona-Version`. Keep any session token server-side until delivered to the intended client through a protected channel.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, resume, approve, decline, redact, rotate, revoke, deploy, or otherwise mutate production Persona resources without explicit operator approval.

## Output

- One redacted create-request fingerprint and inquiry ID
- Observed inquiry status and optional session-token disposition
- Pass/fail smoke-test receipt separated from identity outcome

Return the environment, resource and event identifiers, API version, template context, source-contract fingerprint, evidence, unresolved risk, rollback state, and final decision without exposing bearer keys, webhook secrets, inquiry session tokens, raw identity documents, or unnecessary PII.

## Examples

A CI operator creates one inquiry from template `itmpl_…` with operation key `smoke-<run-id>`, requests a session, asserts a JSON:API inquiry object, and records the returned session token only as present or absent.

## Error Handling

| Failure | Response |
| --- | --- |
| 400 create error | Check JSON:API shape, template selector exclusivity, and environment ownership. |
| 409 or replay mismatch | Compare the stored request fingerprint; never reuse an idempotency key with changed parameters. |
| Inquiry remains pending | That is a valid transport result; use sandbox controls or the supported client flow rather than inventing a pass. |

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
