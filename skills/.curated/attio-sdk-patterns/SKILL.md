---
name: attio-sdk-patterns
description: >-
  Build a typed Attio REST client with tenant-aware tokens, endpoint-specific pagination, structured errors, bounded retries, and contract tests while distinguishing it from the Attio App SDK. Use when creating or refactoring Attio integration code. Trigger with "Attio SDK", "Attio client wrapper", or "typed Attio API".
argument-hint: "[repository-path] [language-or-runtime]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- attio
- sdk
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# Attio Typed Client Patterns

## Overview

This skill designs a small REST client around the endpoints an application actually uses. It does not conflate a server-side REST wrapper with Attio's `attio` App SDK for in-product apps.

## Prerequisites

- Runtime, package manager, and existing HTTP conventions
- Exact endpoints, methods, scopes, and response shapes
- Tenancy and credential model
- Existing tests and error-handling policy

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect clients, types, dependency policy, and tests. Use `WebFetch` only for official Attio REST, OpenAPI, and App SDK documentation. Use `Write` or `Edit` after the target abstraction and endpoint contracts are confirmed.

## Current Contract

- Attio REST requests use the `https://api.attio.com/v2` base URL and endpoint-specific scopes.
- Pagination is endpoint-specific: some operations use limit and offset, while others return a cursor such as `pagination.next_cursor`.
- The Attio App SDK package `attio` serves apps running inside Attio and is not a universal REST client replacement.
- Generated types can start from the official OpenAPI document, but application-level validation and tests still own runtime safety.

## Authentication

Inject a token provider that resolves the authorized workspace at request time. Do not place a global production token in source, client constructors, snapshots, fixtures, or logs.

## Instructions

1. Inventory call sites and group the smallest useful endpoint surface.
2. Reverify each method, path, scope, body, response, and paginator in official documentation.
3. Define typed request and response boundaries with runtime validation for external data.
4. Centralize base URL, authorization, timeouts, redaction, request IDs, and structured error translation.
5. Implement separate offset and cursor iterators; bind each endpoint explicitly to the correct strategy.
6. Retry only eligible transient failures, respecting rate limits and mutation idempotency.
7. Add fixture, pagination-termination, error, redaction, and tenant-isolation tests.

## Approval Boundaries

Do not replace an established client, add a generated dependency, or migrate production call sites without owner approval and compatibility evidence.

## Output

Return the endpoint inventory, client interface, pagination mapping, error taxonomy, auth boundary, test evidence, migration plan, and rollback point.

## Error Handling

| Condition | Response |
|---|---|
| Endpoint contract is ambiguous | Stop and recheck the official endpoint reference. |
| Runtime payload fails validation | Return a typed contract error and preserve redacted evidence. |
| Pagination repeats a page | Abort at the loop guard and record the endpoint strategy. |
| Tenant token does not match context | Reject before sending the request. |

## Examples

Input:

```text
runtime=TypeScript; endpoints=record query and task create; tenancy=multi-workspace
```

Expected handoff:

```text
client=typed REST wrapper; pagination=endpoint mapped; tenant-tests=pass
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [OpenAPI specification](https://docs.attio.com/rest-api/endpoint-reference/openapi)
- [Pagination](https://docs.attio.com/rest-api/guides/pagination)
- [App SDK overview](https://docs.attio.com/sdk/deep-dives/overview)
