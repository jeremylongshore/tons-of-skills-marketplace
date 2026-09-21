---
name: instantly-sdk-patterns
description: >-
  Use the official beta Instantly TypeScript SDK with pinned versions, typed resources, and safe error handling. Use when implementing or reviewing a Node.js client against API v2. Trigger with "use the Instantly TypeScript SDK", "build an Instantly Node client", or "handle Instantly SDK errors".
argument-hint: "[repository-path] [resource]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- sdk-patterns
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Instantly Official SDK Patterns

## Overview

Adopt @instantlyai/sdk without inventing resource methods or hiding HTTP failure semantics. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- The official package is @instantlyai/sdk and remains beta before stable 1.0.0.
- The SDK requires Node.js 22 or later and throws ResponseError for non-success responses.
- Resource coverage is generated from the OpenAPI schema and may evolve during beta.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Inspect runtime and lockfile compatibility before installing the beta package.
2. Confirm the current beta version and pin the resolved lockfile.
3. Create Instantly with a server-side apiKey and no browser exposure.
4. Use generated resource methods and request types that exist in the installed version.
5. Handle ResponseError by status while redacting response bodies and authorization.
6. Add contract tests and a deliberate upgrade review for every beta change.

## Approval Boundaries

Do not create, rotate, reveal, or revoke keys; invite or remove members; delegate across workspaces; connect sending accounts; create or activate campaigns; import or delete leads; change suppression or retention; register, patch, resume, or delete webhooks; alter plans or paid capacity; transmit diagnostics; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace-safe scope, files and contracts inspected, exact API v2 routes and required scopes, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| `401` | Stop and verify that the bearer key exists, is current, and was not revoked. |
| `403` | Stop and compare the operation with its exact required scope; do not broaden to `all:all` by default. |
| `429` | Coordinate the workspace-wide budget, honor endpoint overrides, and bound retries. |
| Schema or tenant mismatch | Fail closed, preserve redacted evidence, and do not retry a mutation. |

## Examples

Use a compact handoff that makes scope, mutation authority, and evidence reviewable.

Input:

```text
runtime=node22; package=@instantlyai/sdk@beta; resource=campaigns
```

Expected handoff:

```text
pin=resolved; types=pass; ResponseError=handled
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
