---
name: canva-advanced-troubleshooting
description: 'Isolate difficult Canva Connect failures without rotating credentials, replaying writes, or leaking customer data. Use when investigating intermittent transport, OAuth, async-job, capability, or preview-feature failures. Trigger with: "deep debug Canva", "Canva intermittent failure", "prepare Canva support evidence".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[incident-id-or-failure-symptoms]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - troubleshooting
  - operations
compatibility: 'Live probes require an approved test user, least-privilege token, and incident-scoped authorization.'
---

# Canva Advanced Failure Isolation

## Overview

Separate application, authorization, provider-contract, asynchronous-job, and network evidence before choosing a recovery action. Preserve the original operation identity and collect only redacted facts.

## Prerequisites

- Incident identifier, first-observed time, and affected operation
- Current integration configuration and pinned OpenAPI version
- Approved synthetic reproduction user and evidence destination

## Instructions

### Step 1: Freeze the failing operation

Record method, endpoint pattern, environment, opaque operation or job identifier, expected terminal state, and last known good release. Do not copy raw payloads or URLs.

### Step 2: Inspect local evidence

Use Read and Grep to compare sanitized logs, deployment/config revisions, token metadata timestamps, scope policy, and the pinned response schema.

### Step 3: Classify the boundary

Distinguish transport failure, HTTP/provider error, OAuth expiry or revocation, missing explicit scope, unavailable capability, preview drift, and an asynchronous job still in progress.

### Step 4: Reproduce read-only

Use a dedicated test user for the smallest non-mutating check. Never refresh a token merely to diagnose unless the credential owner authorizes rotation and atomic storage is available.

### Step 5: Reconcile before retry

Query the existing job or resource where the contract permits. Do not recreate a design, export, upload, or autofill job until duplicate impact and idempotency are resolved.

### Step 6: Escalate with a safe receipt

Provide Canva support only the integration ID, UTC window, endpoint pattern, redacted error code, opaque request/job reference, contract version, and bounded reproduction result.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

A production export intermittently remains in progress. The operator correlates the same job ID with deployment and provider evidence, pauses new submissions, and escalates without attaching the design or token.

## Error Handling

| Failure | Response |
| --- | --- |
| No stable operation ID | Stop mutation and recover the application ledger first |
| OAuth state unclear | Route to the credential owner; do not test by printing or exchanging secrets |
| Preview contract changed | Disable the preview path and compare current first-party docs |
| Support asks for sensitive data | Redact or decline and provide opaque references instead |

## Resources

- [First-party source notes](references/official-docs.md)
- [Error responses](https://www.canva.dev/docs/connect/error-responses/)
- [API request model](https://www.canva.dev/docs/connect/api-requests-responses/)
