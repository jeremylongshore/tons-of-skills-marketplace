---
name: linear-local-dev-loop
description: >-
  Build a fast Linear integration development loop using fixtures, contract boundaries, and an isolated test workspace. Use when iterating locally without polluting production Linear data. Trigger with "develop Linear locally", "mock Linear GraphQL", or "test Linear webhooks locally".
argument-hint: "[repository-path] [graphql|sdk|webhook]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- local-development
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Local Development Loop

## Overview

Keep routine tests deterministic and offline, then use a deliberate read-only or sandbox-workspace probe to detect contract drift.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- Webhook delivery requires a publicly accessible HTTPS, non-localhost URL; localhost-only receivers are not a production-equivalent test.
- Signature verification requires the exact raw request body, so body-parser ordering belongs in local contract tests.
- GraphQL introspection and official generated SDK types are better schema authorities than hand-written guessed fixtures.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Inspect the repository's test framework, GraphQL client boundary, fixtures, environment loading, and webhook middleware order.
2. Record minimal redacted success, partial-error, auth-error, throttling, pagination, and webhook fixtures.
3. Inject a fake client at the adapter boundary; do not mock every SDK model method across the application.
4. Test raw-body signature verification, duplicate delivery IDs, five-second acknowledgement behavior, and queued processing.
5. Use an isolated workspace and approved tunnel only for explicit end-to-end checks; label and clean up test records.
6. Add a protected contract probe that detects schema/package drift without mutating production.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| Fixture contains customer data | Replace it with a synthetic equivalent and purge retained copies. |
| Signature fails locally | Confirm the raw bytes reach verification before JSON parsing. |
| Tunnel unavailable | Run signed synthetic requests locally and defer the real-delivery proof. |
| Test reaches production | Fail closed unless the protected live-test gate is explicitly enabled. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
adapter=graphql; fixtures=synthetic; webhook=raw-body; live=false
```

Expected handoff:

```text
unit=offline; contract=deterministic; production-writes=blocked
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
