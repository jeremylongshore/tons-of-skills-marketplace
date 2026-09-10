---
name: salesloft-common-errors
description: >-
  Classify Salesloft API failures from status, documented error envelopes, auth context, visibility, and rate metadata without exposing customer data. Use when an integration returns 401, 403, 404, 422, 429, or 5xx. Trigger with "Salesloft error", "Salesloft request failed", or "debug Salesloft API".
argument-hint: "[repository-path] [redacted-error]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- salesloft
- troubleshooting
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Salesloft Error Triage

## Overview

This skill identifies the failing contract before changing code, scopes, or credentials. It retains structured error meaning while excluding Bearer values and sales-record payloads.

## Prerequisites

- Method, path template, status, timestamp, and team alias
- Redacted request shape and response content type
- Auth flow, granted scopes, and acting-user role
- Rate headers and attempt count when present

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to trace request construction and response handling. Use `WebFetch` only for the exact official Salesloft contract. Use `Write` or `Edit` after the failure class is supported by evidence.

## Current Contract

- Success data is under `data`; list metadata is under `metadata`.
- Salesloft documents a singular `error` for 403 and 404 responses.
- A 422 response uses a field-keyed `errors` object and can report multiple validation failures.
- A 429 should be evaluated with `x-ratelimit-endpoint-cost` and `x-ratelimit-remaining-minute` plus any retry guidance actually returned.

## Authentication

Record only auth type, expiry state, scope names, and acting-user identity. Never capture an access token, refresh token, client secret, API key, or authorization code.

## Instructions

1. Reproduce once with secrets and record values redacted before persistence.
2. Confirm base URL, method, path, content type, query encoding, and timeout.
3. Classify authentication, permission/visibility, missing resource, validation, rate, transport, or provider failure.
4. Compare the exact endpoint's required scope and allowed parameters with the request.
5. Apply the smallest correction and rerun a read-only or fixture proof first.
6. For writes, require payload approval and read-after-write verification.

## Approval Boundaries

Do not rotate credentials, broaden scopes, change production data, or retry an uncertain write merely to test a theory. Escalate when the failure cannot be reproduced safely.

## Output

Return a redacted symptom, evidence, failure class, smallest supported correction, safe verification, and escalation owner.

## Error Handling

| Status | Response |
|---|---|
| 401 | Check credential expiry and Bearer injection; refresh or reacquire once. |
| 403/404 | Preserve singular `error`; verify scope, visibility, team, and path. |
| 422 | Preserve every field in `errors`; correct only validated inputs. |
| 429/5xx | Bound retries, retain rate state, and surface exhaustion. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
status=422; class=validation; fields=email_address; secrets=redacted; retry=no
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Request and response format](https://developers.salesloft.com/docs/platform/api-basics/request-response-format/)
- [Rate limits](https://developers.salesloft.com/docs/platform/api-basics/rate-limits/)
