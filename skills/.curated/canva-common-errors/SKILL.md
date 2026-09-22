---
name: canva-common-errors
description: 'Analyze and classify Canva Connect failures by HTTP status, provider error code, operation, and authorization state. Use when deciding whether to refresh, reauthorize, wait, reconcile, correct input, or escalate. Trigger with: "Canva API error", "Canva 401", "Canva 403 or 429".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[status-code-and-redacted-error]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - errors
  - operations
compatibility: 'Diagnosis may use redacted production evidence; any live reproduction requires an approved test user and operation.'
---

# Canva Error Classification

## Overview

Treat HTTP status alone as insufficient. Use the current endpoint reference and redacted provider error code to separate caller defects, authorization failures, throttling, preview drift, and provider incidents.

## Prerequisites

- HTTP status, provider error code, endpoint pattern, and UTC window
- Opaque request, resource, or job reference without payload content
- Pinned OpenAPI or endpoint documentation version

## Instructions

### Step 1: Capture a minimal envelope

Record method, endpoint pattern, status, provider code, terminal job state, retry metadata if actually present, and deployment version. Exclude tokens, bodies, signed URLs, and customer identifiers.

### Step 2: Handle authentication failures

For an invalid or expired access token, serialize the authorized refresh flow and atomically store the replacement refresh token. Reauthorize after revocation or unrecoverable refresh failure.

### Step 3: Handle authorization failures

Compare the operation with explicit granted scopes, resource ownership, capabilities, tenant policy, and preview availability. Never assume a write scope grants its read counterpart.

### Step 4: Handle throttling

Pause only the affected endpoint/user queue. Use documented endpoint metadata and response instructions; otherwise apply bounded exponential backoff with jitter rather than a guessed fixed delay.

### Step 5: Handle async failures

Poll the existing job to a documented terminal state. Correct validation or entitlement errors before any new submission.

### Step 6: Escalate provider failures

Correlate repeated server errors with Canva status/changelog and provide a redacted support receipt after bounded retry is exhausted.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

An autofill returns HTTP 403. The operator checks explicit scopes, current capability and Enterprise availability, template ownership, preview status, and the provider error before deciding whether reauthorization is relevant.

## Error Handling

| Failure | Response |
| --- | --- |
| Only HTTP status is available | Collect the redacted provider envelope before acting |
| Refresh repeats 401 | Stop and require reauthorization instead of looping |
| 429 has no retry metadata | Use the local bounded backoff policy and lower concurrency |
| Job failed validation | Correct the request; do not retry unchanged input |

## Resources

- [First-party source notes](references/official-docs.md)
- [Error responses](https://www.canva.dev/docs/connect/error-responses/)
- [OAuth scopes](https://www.canva.dev/docs/connect/appendix/scopes/)
