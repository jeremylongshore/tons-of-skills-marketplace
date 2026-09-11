---
name: bamboohr-common-errors
description: >-
  Triage BambooHR failures by typed status, request ID, operation, permissions,
  retryability, and data risk. Use when an SDK or HTTP call returns an error or
  an apparently successful response is incomplete. Trigger with "BambooHR 401",
  "BambooHR 403", "BambooHR 429", or "debug BambooHR error".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<status-or-exception> <operation>"
version: 1.5.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, hr, bamboohr, errors, troubleshooting]
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# BambooHR Error Triage

## Overview

Diagnose from evidence, not guessed endpoint behavior. Preserve the request ID
and operation while excluding credentials and HR payloads. A `200` with missing
fields may still be a permission/schema issue on legacy report paths.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The tenant, identity, and data scope only when approved live work is in scope.
- The current evidence register plus customer-specific permissions and agreements.

## Current Contract

The official Python SDK defines typed exceptions for bad request, authentication,
permission, not found, timeout, conflict, payload size, media type, validation,
rate limit, and server/network failures. Its request ID may come from any of
three documented response headers. Automatic retry is limited to 408, 429, 504,
and 598—not every `5xx`.

## Authentication

Record only auth mode and credential alias/age. For OAuth `401`, allow one
controlled refresh when configured; persist rotated tokens. For API-key `401`,
verify owner, tenant, and revocation without printing the key. A `403` usually
requires permission analysis, not a retry.

## Instructions

1. Capture timestamp, tenant alias, operation, method/path template, status or
   typed exception, request ID, attempt count, latency, and a redacted summary.
2. Reproduce against a fixture first. If a live retry is needed, obtain approval
   and ensure the operation is read-only or idempotent.
3. Classify:
   - `400`/`422`: validate body, field IDs, filters, pagination, and media type.
   - `401`: validate credential/refresh lifecycle and tenant.
   - `403`: compare required endpoint/field permissions with the owning identity.
   - `404`: distinguish resource, tenant, format, and deprecated-path failures.
   - `409`/`412`: refresh current HR state or policy; do not overwrite.
   - `413`: shrink page, field set, or upload.
   - `429`: honor `Retry-After` when supplied and consume the retry budget.
   - `500`/`502`/`503`: record request ID and service condition; retry only when
     the operation and current client policy explicitly allow it.
   - `504`/`598`: bounded backoff for idempotent work, then queue/defer.
4. Compare current OpenAPI and SDK version before changing code. Do not paper
   over a deprecated endpoint with an unlimited retry.
5. Add a regression test that proves classification, redaction, and behavior.

## Tool Discipline

Use Read, Glob, and Grep to inspect the failing code, schema, and bounded logs.
Use Write/Edit only for an approved fix and regression test. This skill does not
authorize live retries or permission changes.

## Approval Boundaries

Require approval before a production reproduction, mutation retry, credential
rotation, permission change, or sharing any evidence outside its current system.

## Output

Return classification, request ID, likely contract layer, evidence, retry/no-
retry decision, safe reproduction, proposed fix, regression result, owner, and
remaining approval.

## Error Handling

- No status/request ID: preserve transport exception and narrow correlation window.
- Error text contains PII: redact it and retain only a local protected reference.
- Ambiguous mutation outcome: read current state before any retry.

## Examples

- `403` on one field prompts field-permission comparison, not admin elevation.
- `503` is reported as service unavailable; it is not mislabeled as a published quota.

## Resources

Read [official evidence](references/official-docs.md) for current error behavior.
