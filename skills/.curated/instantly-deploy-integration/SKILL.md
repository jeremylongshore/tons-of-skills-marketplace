---
name: instantly-deploy-integration
description: >-
  Deploy an Instantly API v2 integration with scoped secrets, staged verification, and rollback controls. Use when promoting reviewed integration code into staging or production. Trigger with "deploy an Instantly integration", "release Instantly API changes", or "roll back an Instantly deployment".
argument-hint: "[environment] [release-sha]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- deploy-integration
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Deploy an Instantly Integration

## Overview

Promote a tested integration while separating deploy approval from campaign, account, and webhook mutations. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- API keys belong in server-side secret storage and require least-privilege scopes.
- The official SDK is beta and requires Node.js 22 or later; the CLI requires Node.js 18 or later.
- Deployment success does not authorize campaign activation or webhook replacement.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Pin runtime, official SDK or CLI version, OpenAPI assumptions, and release SHA.
2. Provision an environment-specific key through the approved secret manager.
3. Run offline contract tests and a read-only staging smoke test.
4. Deploy with health checks, bounded concurrency, and redacted logs.
5. Verify workspace identity, account/campaign reads, and webhook receiver health.
6. Record rollback criteria and seek separate approval for production data-plane mutations.

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
environment=staging; release=abc123; activate=false
```

Expected handoff:

```text
deploy=healthy; smoke=pass; mutations=not-authorized
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
