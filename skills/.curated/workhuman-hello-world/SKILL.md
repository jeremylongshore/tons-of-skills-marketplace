---
name: workhuman-hello-world
description: 'Verify a Workhuman tenant integration safely with entitlement discovery, a read-only capability check, and a mutation preview. Use when running a first connection or smoke test. Trigger with "test Workhuman safely".'
argument-hint: "[tenant] [integration-purpose]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.4.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, workhuman, smoke-test, verification, onboarding]
model: inherit
effort: medium
compatibility: Designed for Claude Code; tenant reads and recognition mutations require customer-authorized documentation and approval
---
# Safe Workhuman Capability Smoke Test

## Overview

Prove identity, entitlement, and one read-only capability before proposing any recognition, award, worker, or integration change.

## Prerequisites

- An approved access path from `workhuman-install-auth`
- Current tenant documentation for the exact capability being tested
- A synthetic or explicitly approved test identity and a named program owner

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect configuration, `WebFetch` to verify current first-party and tenant contracts, and `Write` or `Edit` only for fixtures and redacted receipts.

## Current Contract

Workhuman publicly describes Social Recognition, a points-based Store, administrator controls, an open API, and managed integrations. Public material does not establish the baseline pack's `/api/v1/*` routes, payload fields, award levels, visibility values, or status sequence.

## Authentication

Use only the documented principal and authorization method for the selected tenant capability. Never substitute an SSO cookie or a guessed bearer-token exchange.

## Instructions

1. Freeze the test objective, tenant, principal class, expected entitlement, and zero-write boundary.
2. Fetch the current authorized contract and record its date, owner, environment, and exact read-only operation.
3. Validate the host and path against an allowlist; reject placeholders and production if the approval names a test environment.
4. Use synthetic identifiers or an approved test identity and request only the minimum response fields.
5. Execute one documented read-only probe; record status, latency, schema fingerprint, and redacted correlation identifier.
6. Compare the response with the documented contract and distinguish empty success from authorization or eligibility failure.
7. Draft—but do not execute—a recognition or integration mutation preview with approver, idempotency, and rollback.

## Approval Boundaries

Do not submit recognition, approve awards, change worker data, redeem points, or enable integrations during this smoke test.

## Output

Return the contract reference, identity and entitlement result, sanitized probe receipt, schema observations, mutation preview, and an explicit `READY` or `BLOCKED` decision.

## Error Handling

| Condition | Response |
|---|---|
| Host, route, or auth differs from documentation | Stop; resolve the contract mismatch before sending another request. |
| Read returns no records | Confirm that empty success is valid before treating it as an access failure. |
| Test identity is not eligible | Preserve the evidence and ask the program owner for an approved fixture. |

## Example

A redacted completion receipt might look like this:

```text
tenant=customer-test; capability=recognition-read; principal=service; result=200-empty-valid; mutation=preview-only; decision=READY
```

## Resources

- [Workhuman Social Recognition](https://www.workhuman.com/platform/social-recognition/)
- [Workhuman integrations](https://www.workhuman.com/capabilities/integrations/)

## Next Steps

Move to the applicable workflow only after the owner approves the exact mutation preview.
