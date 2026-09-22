---
name: canva-hello-world
description: 'Verify a Canva Connect integration with a minimal read-only identity request and a redacted receipt. Use when proving OAuth, endpoint reachability, and response shape before any design or asset mutation. Trigger with: "test Canva connection", "Canva hello world", "verify Canva auth".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[approved-test-user]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - quickstart
  - operations
compatibility: 'Requires a backend-held access token for a dedicated authorized test user.'
---

# Canva Read-Only Connection Proof

## Overview

Prove the smallest safe path first. A successful identity or profile read confirms connectivity and authorization shape but does not authorize design creation, export, assets, or other scopes.

## Prerequisites

- Configured Canva integration and exact redirect URI
- Approved test user with the minimum identity/profile scope
- Backend secret storage and redacted evidence destination

## Instructions

### Step 1: Confirm backend boundary

Use Read and Grep to verify token exchange and storage stay server-side, the target base URL is exact, and no credential appears in client code.

### Step 2: Select the read

Choose the minimum users/me or profile request supported by the granted explicit scope. Do not add design-write scopes for this proof.

### Step 3: Send one request

Use the existing reviewed HTTP adapter and a bounded timeout. Do not print the Authorization header, response body, email, profile, or token metadata.

### Step 4: Validate shape

Check status, content type, required response envelope, and only the minimum opaque identity field needed for correlation.

### Step 5: Classify failure

Separate transport, invalid token, missing explicit scope, revoked consent, malformed response, and provider error using the redacted envelope.

### Step 6: Record success

Use Write or Edit to save integration/config version, endpoint pattern, status category, schema result, latency bucket, and redaction check.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

A new staging integration performs one users/me request for its dedicated test user and records only HTTP success, schema version, and an opaque internal connection reference.

## Error Handling

| Failure | Response |
| --- | --- |
| Token is client-visible | Stop and move the flow to a backend |
| Read returns forbidden | Compare the exact scope and consent; do not add broad scopes blindly |
| Response contains unexpected fields | Reject or ignore according to the pinned schema |
| Proof requires a write | Redesign it around a supported non-mutating request |

## Resources

- [First-party source notes](references/official-docs.md)
- [Quickstart](https://www.canva.dev/docs/connect/quickstart/)
- [Users APIs](https://www.canva.dev/docs/connect/api-reference/users/)
