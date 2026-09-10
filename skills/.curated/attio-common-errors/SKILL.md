---
name: attio-common-errors
description: >-
  Diagnose Attio REST API failures from status, structured error fields, endpoint contract, and request context without exposing customer data. Use when an Attio request returns 400, 401, 403, 404, 409, 422, 429, or 5xx. Trigger with "Attio error", "Attio request failed", or "debug Attio API".
argument-hint: "[repository-path] [status-or-error-code]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- attio
- troubleshooting
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Attio Error Triage

## Overview

This skill classifies an Attio failure before changing code or credentials. It preserves the response's structured fields while keeping tokens and CRM values out of diagnostics.

## Prerequisites

- The HTTP method, path template, status, and redacted response body
- The endpoint's documented required scopes
- The request's pagination mode and mutation semantics
- A correlation or application request identifier when available

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to locate the caller, response parser, retry policy, and logs. Use `WebFetch` only for current official Attio documentation. Use `Write` or `Edit` only after the failing contract and safe verification path are known.

## Current Contract

Attio error responses can include `status_code`, `type`, `code`, and `message`. Diagnose from observed fields instead of inventing a fixed code list; endpoint references remain authoritative for request shape and scopes.

## Authentication

Confirm that a Bearer token exists at runtime and belongs to the intended workspace. For 401, rotate or replace the invalid credential; for 403, compare granted scopes with the endpoint's required scopes before requesting any change.

## Instructions

1. Capture method, path template, status, response content type, and redacted structured error fields.
2. Reconcile the request with the exact endpoint reference, including path slug versus UUID and body envelope.
3. Classify authentication, authorization, validation, uniqueness, not-found, throttling, or provider failure.
4. For 429, parse `Retry-After` as an HTTP date and retry only after the indicated time.
5. For ambiguous 5xx failures, preserve a minimal reproduction and check Attio status before changing business logic.
6. Apply the smallest correction and repeat the same bounded request.

## Approval Boundaries

Do not broaden scopes, rotate a shared production credential, replay an ambiguous mutation, or expose customer payloads while troubleshooting without the responsible owner and a recovery plan.

## Decision Table

| Signal | Likely class | Safe next check |
|---|---|---|
| 400 or 422 | Shape or attribute-value validation | Compare body and attribute type with endpoint docs. |
| 401 | Missing or invalid token | Inspect credential injection without printing the token. |
| 403 | Insufficient scope | Compare exact required scopes. |
| 404 | Wrong resource identifier | Resolve current object, list, record, or entry ID. |
| 409 | Uniqueness conflict | Inspect the documented uniqueness boundary. |
| 429 | Global or score-based throttle | Honor `Retry-After`; simplify expensive queries. |
| 5xx | Provider or transient failure | Bound retries and retain redacted evidence. |

## Output

Return a redacted failure fingerprint, diagnosis, evidence, minimal correction, replay result, and any remaining uncertainty.

## Error Handling

| Condition | Response |
|---|---|
| Response is not JSON | Preserve status and content type; do not force JSON parsing. |
| Token appears in evidence | Stop and redact before storing or sharing it. |
| Retry repeats a permanent 4xx | Stop retrying and fix the request contract. |
| Resource identity is uncertain | Resolve it with a read-only discovery request. |

## Examples

Input:

```text
method=POST; path=/v2/objects/companies/records/query; status=403; code=forbidden
```

Expected handoff:

```text
class=authorization; missing-scope=confirmed-from-endpoint; replay=pass
```

This result ties the correction to endpoint evidence and a safe replay.

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Authentication](https://docs.attio.com/rest-api/guides/authentication)
- [Rate limiting](https://docs.attio.com/rest-api/guides/rate-limiting)
- [REST API overview](https://docs.attio.com/rest-api/overview)
