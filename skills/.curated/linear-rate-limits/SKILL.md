---
name: linear-rate-limits
description: >-
  Implement Linear request, endpoint, and GraphQL complexity budgets with reset-aware throttling. Use when coordinating workers or recovering from RATELIMITED errors. Trigger with "handle Linear rate limits", "budget Linear complexity", or "throttle Linear workers".
argument-hint: "[service] [api-key|oauth|unauthenticated]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- rate-limits
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Request and Complexity Control

## Overview

Coordinate the applicable user, app-actor, endpoint, and complexity budgets so retries do not multiply pressure.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- API key: 2,500 requests and 3,000,000 complexity points per user per hour; OAuth: 5,000 requests and 2,000,000 points per user or app user per hour.
- Unauthenticated traffic: 600 requests and 100,000 complexity points per IP per hour; one query is capped at 10,000 points.
- Endpoint-specific limits can be lower and expose their own limit, remaining, reset, and endpoint-name headers.
- GraphQL throttling returns HTTP 400 with `extensions.code: RATELIMITED`; Linear uses a leaky-bucket refill model.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Inventory every producer and auth actor sharing a quota, including multiple keys owned by the same user.
2. Read request, endpoint, and complexity headers and convert reset values from UTC epoch milliseconds.
3. Allocate per-workload budgets below all applicable limits and centralize queue/admission control.
4. Reject queries above the single-query maximum before sending; reduce fields, nesting, and page size.
5. On `RATELIMITED`, stop new pressure, honor the relevant reset/window evidence, and bound retry attempts with jitter.
6. Test burst, sustained, endpoint-specific, complexity, and retry-storm behavior with synthetic workloads.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| `RATELIMITED` | Identify which request/endpoint/complexity budget failed, then honor its reset evidence. |
| Headers missing | Use a conservative circuit breaker and surface unknown capacity. |
| Multiple keys, one user | Treat them as one API-key quota; do not shard around the limit. |
| Dynamic workspace limit | Use observed headers as authority rather than a cached entitlement. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
auth=api-key; workers=4; target-requests-hour=2000; query-max=8000
```

Expected handoff:

```text
shared-budget=enabled; endpoint-overrides=tracked; retries=bounded
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
