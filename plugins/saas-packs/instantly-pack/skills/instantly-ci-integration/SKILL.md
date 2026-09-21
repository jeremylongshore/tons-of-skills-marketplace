---
name: instantly-ci-integration
description: >-
  Gate Instantly API v2 integrations with offline schema checks and a bounded read-only smoke test. Use when adding Instantly to CI, validating generated clients, or probing a staging workspace. Trigger with "add Instantly CI checks", "validate Instantly OpenAPI", or "smoke-test Instantly staging".
argument-hint: "[repository-path] [offline|staging]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- ci-integration
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Instantly API Contract CI

## Overview

Build a CI lane that catches request, scope, pagination, and response-shape drift before deployment. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- API keys are bearer tokens with endpoint-specific scopes.
- Default workspace limits are 100 requests per second and 6,000 per minute; endpoint overrides still apply.
- Live CI probes must use a non-production workspace and read-only scopes.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Inventory every Instantly call and map it to an API v2 operation and required scope.
2. Validate request fixtures offline against pinned OpenAPI-derived types.
3. Test 401, 403, 429, pagination, timeout, and redaction behavior.
4. Permit one bounded staging list request only when CI secrets and owner approval exist.
5. Fail on schema drift, secret output, unbounded pagination, or mutation attempts.
6. Publish the tested SDK/CLI version, fixtures, and rollback owner.

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
mode=offline; surfaces=campaigns,accounts; mutation=forbidden
```

Expected handoff:

```text
contracts=pass; live-smoke=skipped; secrets=redacted
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
