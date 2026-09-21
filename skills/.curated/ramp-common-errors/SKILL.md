---
name: ramp-common-errors
description: >-
  Analyze and resolve Ramp API failures using status, error_v2, x-trace-id, OAuth scope, and retry safety. Use when an integration returns 400, 401, 403, 404, 422, 429, 5xx, or 504. Trigger with "Ramp API error" or "Ramp forbidden".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, errors, debugging, operations]
---
# Ramp API Error Triage

## Overview

Turn a failing request into a sanitized, reproducible diagnosis. Separate permanent request or authority failures from transient service conditions before retrying anything.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Ramp returns standard HTTP status codes and may include `error_v2.error_code`, `additional_info`, and a user-facing message.
- Every API response includes `x-trace-id`; preserve it for correlation and support without logging authorization or sensitive payloads.
- 401 indicates a missing, expired, or invalid token; 403 indicates a valid token without sufficient scope or resource authority.
- 429 and 5xx may be retried with bounded exponential backoff; 504 means the request crossed Ramp's 60-second timeout.

## Instructions

1. Capture method, sanitized URL, status, response class, `x-trace-id`, attempt count, environment, grant type, and requested scope without recording secrets or raw sensitive bodies.

2. Validate the request against the current endpoint schema, including required and nested fields; never rely on an unknown field being ignored.

3. For 401, refresh or reacquire the appropriate token once. For 403, compare configured scopes, token-bound scopes, app grant, user role, entity access, and endpoint authority.

4. For 429, 5xx, or 504, retry only idempotent reads or writes protected by an idempotency key, using bounded exponential backoff and jitter.

5. Reproduce in sandbox with the smallest sanitized request, preserve the trace ID and outcome, and escalate persistent vendor-side failures with the evidence bundle.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

The integration owner approves any request correction. Security approves credential rotation; finance or workflow owners approve replay of a write with business effects.

## Output

A failure classification, sanitized reproducer, trace ID, authority comparison, retry/replay decision, fix, and post-fix verification.

## Error Handling

| Condition | Response |
|---|---|
| A body contains financial or personal data | Store only a redacted field inventory and one-way identifiers; do not paste the body into tickets. |
| A write timed out after submission | Reconcile the resource or deferred task before retrying; use the original idempotency key. |
| The same call alternates 401 and 403 | Verify environment and token provenance before changing scopes or roles. |

## Examples

### Example 1

Diagnose a 403 transaction read by comparing `transactions:read`, the token's environment, and the authorizing user's access.

### Example 2

Triage a 504 accounting export, reconcile whether the sync receipt exists, then retry only the uncommitted idempotent unit.

## Validation

- The diagnosis distinguishes request, authentication, authorization, rate, timeout, and service failures.
- The evidence includes `x-trace-id` but no secret or sensitive business payload.
- Every retry has a bounded budget and an idempotency/reconciliation rationale.
- The corrected request is verified in sandbox or with an approved read-only production probe.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
