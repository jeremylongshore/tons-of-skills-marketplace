---
name: canva-security-basics
description: 'Implement the Canva Connect security baseline for backend OAuth, least privilege, tenant isolation, logging, revocation, and preview webhook verification. Use when threat-modeling, reviewing, or hardening an integration. Trigger with: "secure Canva integration", "Canva token security", "verify Canva webhook".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[integration-id-and-threat-scope]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - security
  - operations
compatibility: 'Requires a backend web application, approved secret store, threat owner, and current Canva security documentation.'
---

# Canva Integration Security Baseline

## Overview

Protect client secrets and user tokens as separate high-impact credentials. Enforce authorization before provider access and treat preview webhook verification as an additional boundary, not proof of business authorization.

## Prerequisites

- Integration ID, environments, operations, tenants, and threat scope
- Current scopes, redirect URIs, token stores, and data flows
- Webhook/preview use, incident response, secret scanning, and audit controls

## Instructions

### Step 1: Inventory secrets and flows

Use Read and Grep to locate client secrets, access/refresh tokens, PKCE verifier, OAuth state, callbacks, browser bundles, logs, backups, jobs, and external processors.

### Step 2: Harden OAuth

Require controlled redirect hosts, one-time state/verifier, backend token exchange, encrypted and separated tokens, per-user refresh serialization, revocation, and disconnect cleanup.

### Step 3: Minimize authorization

Request explicit minimum scopes and enforce tenant, resource, role, capability, purpose, and preview status server-side before every action.

### Step 4: Harden data and logs

Use Write or Edit to prevent tokens, bodies, signed URLs, personal data, and resource identifiers from routine logs; protect stored content and deletion workflows.

### Step 5: Verify webhooks

For authorized preview use, validate the signed token/claims against cached Canva JWKs, select by case-sensitive key ID, refetch only for unknown keys, enforce replay/idempotency controls, and authorize resulting actions separately.

### Step 6: Harden dependencies and deployment

Pin provider/client inputs, scan secrets, isolate environments, protect CI from forks, deploy immutably, and maintain tested rollback and credential rotation.

### Step 7: Prove controls

Test state mismatch, token leak prevention, cross-tenant denial, refresh races, scope denial, unknown webhook key, replay, revoked consent, and account deletion.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

A valid Canva webhook signature is accepted only as authenticity evidence. The router still checks preview authorization, tenant/resource policy, idempotency, and allowed action before processing.

## Error Handling

| Failure | Response |
| --- | --- |
| Secret reaches public repository | Assume compromise, rotate, and investigate |
| Cross-tenant access succeeds | Disable the path and treat as a security incident |
| Webhook key is unknown | Refetch the public JWK set once and fail closed if still unknown |
| Consent is revoked | Delete tokens and deny queued work |

## Resources

- [First-party source notes](references/official-docs.md)
- [Connect security](https://www.canva.dev/docs/connect/guidelines/security/)
- [Webhook keys](https://www.canva.dev/docs/connect/api-reference/webhooks/keys/)
