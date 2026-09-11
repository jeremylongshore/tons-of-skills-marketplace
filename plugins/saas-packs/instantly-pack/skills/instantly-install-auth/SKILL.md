---
name: instantly-install-auth
description: >-
  Analyze and install pinned official Instantly SDK or CLI tooling and verify a least-privilege API v2 key. Use when operating install auth workflows. Trigger with "instantly install auth", "Instantly API", or "Instantly integration".
argument-hint: "[sdk|cli|http] [workspace]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- install-auth
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Install and Authenticate Instantly Tooling

## Overview

Establish a reproducible server-side client without leaking a key or granting unnecessary scopes. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- The official TypeScript SDK is @instantlyai/sdk beta and requires Node.js 22 or later.
- The official CLI is @instantlyai/cli and supports INSTANTLY_API_KEY for non-interactive use.
- API v2 keys are displayed once and are not compatible with API v1.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Inspect the repository runtime, package manager, lockfile, and existing Instantly client.
2. Choose HTTP, SDK, or CLI deliberately and verify current first-party installation guidance.
3. Pin a compatible version; use the SDK beta tag only while the first-party docs require it.
4. Create a key with only the exact endpoint scopes and store it in an approved secret manager.
5. Verify with one bounded read-only request and distinguish 401 from 403.
6. Record versions, workspace identity, scopes, evidence, rotation owner, and rollback.

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
client=sdk; runtime=node22; scopes=campaigns:read
```

Expected handoff:

```text
package=@instantlyai/sdk; auth=pass; key=redacted
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
