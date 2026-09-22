---
name: salesloft-local-dev-loop
description: >-
  Build a Salesloft integration locally with sanitized contract fixtures, deterministic failure cases, and an optional guarded read-only smoke test. Use when iterating without touching real sales records. Trigger with "Salesloft local dev", "mock Salesloft", or "Salesloft contract fixtures".
argument-hint: "[repository-path] [runtime]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- salesloft
- testing
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Salesloft Local Contract Loop

## Overview

This skill creates a fast local loop around realistic Salesloft envelopes, pagination, errors, and webhook signatures. Live CRM mutation is outside the default loop.

## Prerequisites

- A named repository and test framework
- Sanitized fixtures containing no customer or prospect data
- A replaceable HTTP transport boundary
- Optional non-production read credential stored outside source

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to map the client, adapters, fixtures, and test commands. Use `WebFetch` only to recheck official Salesloft contracts. Use `Write` or `Edit` only inside the confirmed repository.

## Current Contract

- Model successful responses with `data` and list `metadata`.
- Model 403/404 as a singular `error`, 422 as field-keyed `errors`, and 429 with current rate headers.
- Pagination begins at page 1; supported endpoints generally allow `per_page` from 1 through 100.
- Webhook fixtures must preserve exact raw bytes for SHA-1 HMAC verification.

## Authentication

Tests inject a fake Bearer value and assert redaction. An optional live lane may use a read-only credential only when the target team is explicitly named.

## Instructions

1. Identify the smallest HTTP adapter and every response shape the application consumes.
2. Add sanitized success fixtures for identity, paged lists, and empty pages.
3. Add deterministic 401, 403, 404, 422, 429, timeout, and non-JSON cases.
4. Add webhook fixtures with raw body bytes, event header, signature, and callback token.
5. Run unit and contract tests offline on every change.
6. Keep any live smoke lane opt-in, read-only, bounded, and disabled for untrusted forks.

## Approval Boundaries

Never copy production responses into fixtures or use real tokens as placeholders. Do not enable live writes from a local test command.

## Output

Return fixture inventory, contract assertions, commands run, pass/fail results, live-lane state, and any unsupported response shape.

## Error Handling

| Condition | Response |
|---|---|
| Fixture contains PII | Remove it, rotate if necessary, and replace with synthetic data. |
| Test bypasses adapter | Move the call behind the transport seam before mocking. |
| Live lane lacks team guard | Disable it until target identity is asserted. |
| Contract drift | Update the fixture and consumer together with an official-source receipt. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
offline=pass; fixtures=8; live-smoke=disabled; customer-records=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Request and response format](https://developers.salesloft.com/docs/platform/api-basics/request-response-format/)
- [Webhook delivery headers](https://developers.salesloft.com/docs/platform/webhooks/delivery-headers/)
