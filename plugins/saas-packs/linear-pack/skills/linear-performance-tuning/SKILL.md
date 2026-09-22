---
name: linear-performance-tuning
description: >-
  Improve Linear GraphQL latency and throughput by reducing field, connection, pagination, and polling cost. Use when queries are slow, complex, or exhausting shared budgets. Trigger with "optimize Linear GraphQL", "reduce Linear query complexity", or "speed up Linear sync".
argument-hint: "[repository-path] [operation-name]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- performance
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Query Performance Tuning

## Overview

Tune the measured operation rather than applying guessed delays, and preserve correctness with bounded pagination and reconciliation.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- Each property costs 0.1 complexity point, each object 1 point, and connections multiply child cost by the requested page size or default 50, rounded up.
- A single query cannot exceed 10,000 complexity points; hourly complexity and request limits are shared by user or app actor.
- Filtering server-side, requesting explicit page sizes, ordering by updated time, and using webhooks reduce unnecessary work.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Measure operation latency, requested fields, connection fan-out, page sizes, complexity header, payload bytes, and cache hit rate.
2. Replace broad SDK model walks with a purpose-built GraphQL query when only a narrow projection is needed.
3. Filter at the server, request the smallest explicit page, and paginate until `hasNextPage` is false.
4. Eliminate N+1 reads and uncoordinated polling; use webhooks plus a bounded reconciliation window.
5. Load-test below the applicable shared request/complexity budgets and verify tail latency and correctness.
6. Document before/after evidence and rollback the query change if semantics or visibility differ.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| Complexity above 10,000 | Shrink connections, fields, or page size before sending the query. |
| Budget exhausted | Coordinate producers and wait for reset metadata; do not spin retries. |
| Pagination misses data | Use stable cursors and explicit updated-time reconciliation. |
| Cache leaks visibility | Scope keys by workspace/team/access context or disable the cache. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
operation=IssueSync; first=50; nested-connections=3; complexity=measured
```

Expected handoff:

```text
query=narrowed; pagination=cursor; polling=replaced; correctness=verified
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
