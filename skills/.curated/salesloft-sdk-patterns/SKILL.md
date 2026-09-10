---
name: salesloft-sdk-patterns
description: >-
  Analyze and design a typed Salesloft REST adapter with tenant-bound authentication, endpoint-specific schemas, pagination, errors, and rate metadata. Use when creating or refactoring an integration client. Trigger with "Salesloft SDK patterns", "Salesloft client wrapper", or "typed Salesloft API".
argument-hint: "[repository-path] [language]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- salesloft
- api-client
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Salesloft Typed REST Adapter

## Overview

This skill builds a narrow client around the endpoints an application actually uses. It avoids invented universal schemas, implicit tenant state, and unbounded recursive retries.

## Prerequisites

- A repository with an identified HTTP boundary
- Endpoint, scope, request-format, and response-format inventory
- A tenant-to-credential resolver
- Fixture coverage for success and failure envelopes

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect package versions, call sites, and generated types. Use `WebFetch` only for official endpoint contracts. Use `Write` or `Edit` after the adapter boundary is confirmed.

## Current Contract

- Use `https://api.salesloft.com/v2` and documented resource paths; do not force `.json` onto every path.
- Preserve `data`, `metadata`, `error`, and field-keyed `errors` as separate typed shapes.
- Pagination and filters are endpoint-specific; page numbers begin at 1 and deep pages consume more rate cost.
- Capture `x-ratelimit-endpoint-cost` and `x-ratelimit-remaining-minute` from every response that provides them.
- Use the request content type documented by the endpoint rather than assuming all writes are JSON.

## Authentication

Resolve one Bearer credential from the explicit tenant context for every call. Never store a mutable global token or retry with another tenant's credential.

## Instructions

1. Inventory exact methods, paths, scopes, query parameters, bodies, and consumed response fields.
2. Define typed success, list metadata, singular error, validation error, and rate-state models.
3. Centralize timeout, Bearer injection, content negotiation, and redacted error capture.
4. Implement an iterative page iterator that stops on `metadata.paging.next_page` or an empty page.
5. Retry only safe operations or explicitly idempotent application workflows with a bounded attempt budget.
6. Add contract fixtures before migrating callers behind the adapter.

## Approval Boundaries

Do not synthesize request fields from examples, automatically fall back to v1, or retry CRM writes without an application idempotency rule and operator approval.

## Output

Return endpoint inventory, type boundaries, auth resolver, pagination behavior, retry policy, fixture coverage, and remaining direct calls.

## Error Handling

| Condition | Response |
|---|---|
| 401 | Refresh or reacquire through the configured auth flow once. |
| 403/404 | Preserve singular `error` and verify scope, visibility, and path. |
| 422 | Preserve field-keyed `errors`; do not flatten away field context. |
| 429/5xx | Respect current headers and bounded backoff; surface exhaustion. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
tenant=team-42; endpoint=GET /v2/people; pages=2; rate-cost=2; retries=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Request and response format](https://developers.salesloft.com/docs/platform/api-basics/request-response-format/)
- [Filtering, paging, and sorting](https://developers.salesloft.com/docs/platform/api-basics/filtering-paging-sorting/)
