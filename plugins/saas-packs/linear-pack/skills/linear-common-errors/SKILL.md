---
name: linear-common-errors
description: >-
  Diagnose Linear GraphQL and SDK failures from transport, response, and request evidence. Use when an integration returns partial data, authentication failures, rate limits, invalid input, or missing resources. Trigger with "debug Linear GraphQL", "Linear API error", or "why did Linear SDK fail".
argument-hint: "[repository-path] [redacted-error-or-request-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- error-triage
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Error Triage

## Overview

Classify a failure before changing code or credentials, because Linear can return GraphQL errors with HTTP 200 and throttling errors with HTTP 400.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- Always inspect the GraphQL `errors` array; a response can include partial `data` and errors together.
- Rate limiting is identified by `extensions.code: RATELIMITED` in an HTTP 400 GraphQL response, not by assuming HTTP 429.
- The SDK exposes parsed `LinearError` details including query, variables, status, data, raw error, and per-error path/type when available.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Capture the operation name, HTTP status, GraphQL error code/path, SDK version, and redacted rate headers.
2. Separate authentication, authorization, input, not-found, complexity, endpoint-budget, and service-health failures.
3. Reproduce with the smallest read-only query using the same auth mode; do not paste tokens or full customer variables.
4. For partial data, decide whether the caller must reject the whole response or can use explicitly safe fields.
5. For throttling, follow reset metadata, shrink requested fields/pages, and coordinate all workers sharing the user or app budget.
6. Return the root-cause evidence, bounded remediation, and a regression assertion.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| HTTP 200 plus `errors` | Treat it as an application failure unless partial-data handling is explicitly designed. |
| HTTP 400 plus `RATELIMITED` | Honor reset data and reduce request or complexity pressure. |
| Forbidden | Verify team visibility and exact OAuth scope; do not broaden access by default. |
| Unknown schema field | Check introspection, SDK version, and deprecation notices before renaming code. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
status=200; errors[0].path=issueCreate; sdk=95.0.0; variables=redacted
```

Expected handoff:

```text
class=graphql-application-error; retry=no; regression=payload-error-check
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
