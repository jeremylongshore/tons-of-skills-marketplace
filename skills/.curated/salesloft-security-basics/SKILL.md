---
name: salesloft-security-basics
description: >-
  Harden Salesloft tenant isolation, OAuth and API-key storage, least-privilege scopes, CRM-data handling, and webhook verification. Use when reviewing an integration security boundary. Trigger with "Salesloft security", "secure Salesloft tokens", or "Salesloft webhook verification".
argument-hint: "[repository-path] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- salesloft
- security
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Salesloft Integration Security Boundary

## Overview

This skill reviews how credentials, tenant context, prospect data, mutations, and webhook deliveries move through an integration. It produces remediations tied to evidence and named owners.

## Prerequisites

- Architecture, data-flow, scope, and secret inventories
- Named Salesloft teams, environments, and data owners
- Current webhook subscription configuration
- Incident and credential-rotation procedures

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect auth, logging, storage, routing, and signature code. Use `WebFetch` only for official Salesloft security contracts. Use `Write` or `Edit` only after the remediation target is confirmed.

## Current Contract

- Every API credential is a Bearer secret and must remain server-side.
- Authorization-code refresh rotates the refresh token; client credentials have no refresh token.
- API keys act as the issuing customer user and are not the partner application path.
- `x-salesloft-signature` is a hex SHA-1 HMAC of the exact request body using `callback_token` as the key.
- Salesloft does not document a timestamp header in the general delivery-header contract, so do not invent timestamp replay verification.

## Authentication

Bind each encrypted credential record to one Salesloft team, flow, scope set, environment, owner, and rotation state. Fail closed when tenant context is missing or mismatched.

## Instructions

1. Trace credential acquisition, storage, decryption, refresh, injection, revocation, and audit events.
2. Verify least-privilege scopes against every used method and path.
3. Enforce explicit tenant context across queues, caches, jobs, logs, and database keys.
4. Redact Authorization, token, callback-token, email, phone, and CRM fields from diagnostics.
5. Verify webhook HMAC over exact raw bytes with equal-length constant-time comparison.
6. Validate the event type and callback token, then apply durable deduplication before side effects.
7. Test rotation, tenant-confusion, invalid-signature, deletion, and incident paths.

## Approval Boundaries

Do not broaden scopes, export customer data, create or revoke credentials, delete Salesloft records, or rotate production secrets without named owner approval and rollback planning.

## Output

Return tenant and data-flow findings, scope delta, secret lifecycle, webhook-verification result, redaction gaps, prioritized fixes, owners, and verification evidence.

## Error Handling

| Condition | Response |
|---|---|
| Tenant mismatch | Fail closed and investigate cross-team exposure. |
| Signature length differs | Reject before constant-time comparison. |
| Credential exposure | Revoke or rotate, contain logs, and follow incident procedure. |
| Uncertain delete | Stop; Salesloft documents person deletion as not normally reversible. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
tenant-binding=pass; scopes=least-privilege; webhook-hmac=pass; pii-log-gaps=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [API key authentication](https://developers.salesloft.com/docs/platform/api-basics/api-key-authentication/)
- [Webhook delivery headers](https://developers.salesloft.com/docs/platform/webhooks/delivery-headers/)
