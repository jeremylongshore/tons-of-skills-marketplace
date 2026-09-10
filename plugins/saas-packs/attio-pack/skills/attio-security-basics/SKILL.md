---
name: attio-security-basics
description: >-
  Harden an Attio integration with least-privilege credentials, tenant isolation, log redaction, raw-body webhook verification, idempotency, and incident-ready rotation. Use when reviewing Attio security controls or preparing production access. Trigger with "Attio security", "secure Attio integration", or "Attio webhook signature".
argument-hint: "[repository-path] [integration-scope]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- attio
- security
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# Attio Integration Security Baseline

## Overview

This skill audits and hardens Attio authentication, data handling, webhook verification, tenant boundaries, and operational response without exposing secrets or customer records.

## Prerequisites

- Data-flow and trust-boundary inventory
- Endpoint-to-scope map and tenant model
- Secret-store, logging, retention, and incident-response owners
- Webhook receiver code when events are enabled

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect credential flow, authorization, logs, storage, and webhook handling. Use `WebFetch` only for current official Attio security contracts. Use `Write` or `Edit` after findings, target controls, and rollback conditions are approved.

## Current Contract

- Tokens should be least-privilege, stored server-side, tenant-bound, redacted, and rotatable.
- Verify `Attio-Signature` by computing SHA-256 HMAC over the exact raw UTF-8 request body with the webhook secret and comparing equal-length hexadecimal values in constant time.
- The signature input is the raw body only; do not invent a timestamp concatenation protocol.
- Delivery is at least once. Use `Idempotency-Key` and durable state to control duplicates; signature verification alone is not deduplication.

## Authentication

Prefer OAuth for multi-workspace applications and a workspace key for a controlled single workspace. Enforce server-side workspace authorization before resolving the encrypted token.

## Instructions

1. Map secrets, tenant context, Attio data, logs, queues, backups, and administrative paths.
2. Compare used endpoints with granted scopes and remove unjustified privilege through an approved rotation.
3. Enforce tenant authorization before credential resolution and storage access.
4. Redact authorization headers, secrets, raw customer payloads, and sensitive attribute values from telemetry.
5. Preserve the raw webhook body, verify its HMAC before parsing, compare equal-length buffers safely, and reject failures.
6. Deduplicate accepted events by `Idempotency-Key`, queue work, and reconcile downstream state.
7. Exercise token revocation, webhook-secret rotation, audit review, and incident rollback.

## Approval Boundaries

Do not rotate production secrets, reduce retention, change access scopes, or replay customer mutations without the responsible security and service owners.

## Output

Return the threat boundaries, scope gaps, secret lifecycle, webhook verification evidence, redaction tests, tenant-isolation tests, and remediation owners.

## Error Handling

| Condition | Response |
|---|---|
| Raw webhook body is unavailable | Reject the event and fix middleware ordering. |
| Signature lengths differ | Reject before constant-time comparison. |
| Token appears in retained output | Revoke or rotate it and scrub the artifact. |
| Duplicate idempotency key arrives | Acknowledge without repeating committed work. |

## Examples

Input:

```text
scope=oauth service plus webhook receiver; environment=production candidate
```

Expected handoff:

```text
least-privilege=verified; hmac=raw-body; dedupe=durable; rotation=exercised
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Authentication](https://docs.attio.com/rest-api/guides/authentication)
- [Webhooks](https://docs.attio.com/rest-api/guides/webhooks)
