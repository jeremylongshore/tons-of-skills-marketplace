---
name: persona-install-auth
description: >-
  Configure sandbox and production Persona API keys, dated API-version headers, and a least-privilege client boundary. Use when bootstrapping or rotating Persona credentials. Trigger with: "set up Persona auth", "rotate Persona API key", "configure Persona environment".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[environment-and-service]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - persona
  - authentication
  - api-keys
  - environment
compatibility: 'Requires an authorized Persona environment, current first-party documentation, a reviewed dated API version, and privacy-safe operational evidence.'
---

# Persona Environment and Least-Privilege API Key Setup

## Overview

Establish an explicit environment boundary before any identity workflow. Persona API keys are environment-specific, may carry different configured API versions, and must reach `https://api.withpersona.com/api/v1`; a credential check must not create or mutate an inquiry.

## Prerequisites

- Persona Dashboard access authorized for the target environment
- A named service owner, secret store, and rotation window
- The approved dated Persona API version; current documentation shows `2025-12-08`

## Instructions

### Step 1: Inventory the boundary

Record sandbox or production, owning service, inquiry template, API-key permissions, configured API version, and secret-store location. Never infer environment from an untrusted request.

### Step 2: Create and store the key

Create the narrowest key supported by the Dashboard. Put the value in the deployment secret store, expose it only as `PERSONA_API_KEY`, and retain only the key name and final four characters in receipts.

### Step 3: Pin request metadata

Set the base URL to `https://api.withpersona.com/api/v1`. Send `Authorization: Bearer ...`, `Persona-Version: 2025-12-08` or the reviewed target version, `Accept: application/json`, and `Content-Type: application/json` for bodies.

### Step 4: Run a read-only probe

List one inquiry or call another approved read endpoint. Capture status, response request identifier, rate-limit headers, environment, and API version without storing response PII.

### Step 5: Prove separation and rotation

Confirm sandbox and production secrets cannot be swapped by configuration fallback. Exercise dual-secret rollout, old-key revocation, and rollback in sandbox before production.

## Authentication

Persona REST authentication uses an environment-scoped API key as a bearer token. The `Persona-Version` request header overrides the version configured on that key for the request, so pin it deliberately and test each key independently.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, resume, approve, decline, redact, rotate, revoke, deploy, or otherwise mutate production Persona resources without explicit operator approval.

## Output

- Environment-and-service credential inventory
- Redacted read-only connectivity receipt
- Rotation, revocation, and rollback procedure

Return the environment, resource and event identifiers, API version, template context, source-contract fingerprint, evidence, unresolved risk, rollback state, and final decision without exposing bearer keys, webhook secrets, inquiry session tokens, raw identity documents, or unnecessary PII.

## Examples

For a sandbox worker, store `persona_sandbox_…` in the sandbox secret scope, pin the reviewed dated version, list at most one inquiry, and record only status, request ID, and quota headers. A production key is never copied into that scope.

## Error Handling

| Failure | Response |
| --- | --- |
| 401 unauthorized | Check the secret binding, revocation state, and bearer header; do not print the key. |
| 403 or unexpected data | Stop and verify environment, tenant, and key permissions before retrying. |
| Version-dependent response | Compare the explicit `Persona-Version` header with the key’s Dashboard version and the migration fixture. |

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
