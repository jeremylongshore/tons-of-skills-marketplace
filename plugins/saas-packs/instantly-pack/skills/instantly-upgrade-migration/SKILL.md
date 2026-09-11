---
name: instantly-upgrade-migration
description: >-
  Upgrade Instantly SDK, CLI, OpenAPI-derived types, or API v2 contracts with controlled compatibility testing. Use when operating upgrade migration workflows. Trigger with "instantly upgrade migration", "Instantly API", or "Instantly integration".
argument-hint: "[component] [target-version]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- upgrade-migration
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Upgrade Instantly SDK and API Contracts

## Overview

Handle ongoing tooling and schema evolution separately from the one-time API v1 cutover. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- The TypeScript SDK is beta and may receive refinements before stable 1.0.0.
- The CLI and SDK have different Node.js minimums and release cadences.
- Generated resources follow the live OpenAPI schema; method availability must be checked in the installed version.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Inventory current runtime, package pins, generated types, routes, fixtures, and consumers.
2. Read first-party release/package metadata and classify breaking, additive, and behavioral changes.
3. Update one component in an isolated branch and retain the previous lockfile for rollback.
4. Run offline type, contract, error, pagination, and redaction tests.
5. Canary a bounded read-only staging operation.
6. Promote only after owner review; record resolved versions, evidence, and rollback trigger.

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
component=@instantlyai/sdk; from=beta-old; to=beta-current
```

Expected handoff:

```text
tests=pass; staging=pass; production=awaiting-owner
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
