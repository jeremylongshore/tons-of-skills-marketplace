---
name: linear-sdk-patterns
description: >-
  Implement current Linear TypeScript SDK query, mutation, pagination, raw GraphQL, and error-handling patterns. Use when building or refactoring a typed Linear adapter. Trigger with "use Linear SDK", "refactor Linear client", or "write typed Linear GraphQL".
argument-hint: "[repository-path] [query|mutation|pagination|raw-graphql]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- sdk-patterns
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear TypeScript SDK Patterns

## Overview

Keep SDK mechanics inside a bounded adapter and expose domain-shaped results rather than generated model objects throughout the application.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- Current SDK mutations use verb-first names such as `createIssue`, `updateUser`, and `archiveProject`.
- Connections expose `nodes`, `pageInfo`, `fetchNext`, and `fetchPrevious`; optional variables are passed in an object.
- `linearClient.client.rawRequest` supports purpose-built GraphQL, while `LinearError` exposes parsed request/response/error evidence.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Inspect the installed SDK version, generated types, adapter boundary, call sites, and error policy.
2. Create one client per approved auth context and inject it; never construct clients throughout business code.
3. Wrap SDK models in domain functions that accept stable IDs and return minimum typed projections.
4. Paginate every connection explicitly and expose checkpoints for long-running synchronization.
5. Use raw GraphQL only when it measurably reduces fields or fan-out; keep operation names and variables typed.
6. Normalize `LinearError` and GraphQL partial errors into retryable, terminal, and reconciliation-required outcomes.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| Method missing | Compare code with the installed generated SDK and the verb-first mutation contract. |
| Connection truncated | Follow `pageInfo` or SDK page helpers until the required boundary is reached. |
| Model leaks across layers | Map it to a stable application-owned type at the adapter boundary. |
| Raw query drifts | Validate against current introspection/generated schema and add a contract test. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
adapter=issues; operation=listUpdated; page-size=25; checkpoint=cursor
```

Expected handoff:

```text
client=injected; projection=minimal; pagination=explicit; errors=normalized
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
