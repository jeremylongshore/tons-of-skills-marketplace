---
name: clickup-sdk-patterns
description: >-
  Build a typed ClickUp client from official OpenAPI contracts with explicit version routing, auth injection, error typing, pagination, and retry policy. Use when creating a reusable ClickUp adapter. Trigger with "ClickUp SDK", "ClickUp client wrapper", or "typed ClickUp API".
argument-hint: "[repository-path] [language]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- sdk-design
model: inherit
effort: high
compatibility: Designed for Claude Code; live client verification requires a scoped ClickUp credential
---
# ClickUp Typed Client Patterns

## Overview

Keep application code independent of transport details without presenting an ungoverned third-party wrapper as an official SDK.

## Prerequisites

- Pinned official v2 and v3 OpenAPI documents or reviewed endpoint schemas
- A server-side HTTP runtime, validation library, and test framework
- Auth, Workspace, timeout, retry, redaction, and observability policies

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- ClickUp publishes v2 and v3 OpenAPI specifications suitable for generation.
- Route every operation to an explicit version/base path and preserve ClickUp field types, including nullable webhook fields.
- Inject personal or OAuth tokens at call time and never store them in client objects serialized to logs.
- Retry only idempotent transient operations by default; writes need durable application idempotency.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Inventory required operations and pin the matching official schema/version digest.
2. Generate or hand-write a narrow transport and wrap it behind domain-oriented interfaces.
3. Inject auth, Workspace allow-list, timeouts, content type, and redacted telemetry centrally.
4. Create endpoint-specific pagination helpers instead of one incorrect universal iterator.
5. Map statuses/error codes into typed retryable, authorization, plan, validation, and unknown classes.
6. Test fixtures, schema drift, cancellation, retry ceilings, partial writes, and version migration seams.

## Approval Boundaries

Do not auto-generate broad production access, silently fall back between API versions, or retry writes without a durable source key and owner policy.

## Output

Return schema pins, supported operations, version routing, auth boundary, error/pagination policies, test coverage, and unsupported surfaces.

## Error Handling

| Condition | Response |
|---|---|
| Generated client exposes the token | Block release and correct serialization/logging. |
| Schema has breaking drift | Regenerate in a review branch and run contract tests. |
| Endpoint pagination is unknown | Refuse full-scan claims until documented. |
| Write outcome is ambiguous | Reconcile by durable source ID before retry. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
schemas=v2@sha256:...+v3@sha256:...; operations=11; direct-http=0; write-retry=off; contracts=pass
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [OpenAPI specifications](https://developer.clickup.com/docs/open-api-spec)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
