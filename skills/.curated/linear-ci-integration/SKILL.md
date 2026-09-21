---
name: linear-ci-integration
description: >-
  Design Linear-aware CI checks without turning every build into an uncontrolled production mutation. Use when validating a Linear adapter, obtaining a short-lived automation token, or linking CI evidence to work. Trigger with "test Linear in CI", "add Linear contract tests", or "authenticate Linear automation".
argument-hint: "[repository-path] [contract-test|client-credentials|issue-linking]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- ci-integration
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear CI Contract Integration

## Overview

Add deterministic CI coverage around a Linear integration while keeping ordinary pull-request tests offline and production writes explicitly gated.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- For CI and scheduled automation, Linear recommends requesting a client-credentials token at the start of each run instead of persisting an access token as a long-lived key.
- A client-credentials token is an app-actor token, is valid for 30 days, and must be replaced after a 401; requesting different scopes revokes the app's existing app-actor tokens.
- GraphQL transport success does not prove operation success; CI assertions must inspect the response `errors` array and mutation payload.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Inventory existing CI, test doubles, secret providers, and any Linear-aware branch or pull-request convention.
2. Keep pull-request tests offline with recorded, redacted GraphQL fixtures and schema-level assertions.
3. Put any live read probe in a separately approved protected job; acquire the narrowest client-credentials token per run and never echo it.
4. Gate live mutations behind an explicit environment approval and an idempotency key owned by the integration.
5. Assert HTTP status, GraphQL `errors`, expected payload fields, and rate-limit headers; preserve only redacted receipts.
6. Document who can rotate the OAuth client secret, disable the job, and clean up test artifacts.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| Fixture/schema drift | Refresh from a redacted approved response and review the semantic change. |
| 401 in protected job | Discard the token, verify app access, and obtain a new per-run token. |
| GraphQL errors | Fail the job even when HTTP is 200; report code and path without sensitive variables. |
| Mutation may repeat | Stop and add an idempotency or reconciliation contract before retrying. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
mode=contract-test; live-probe=read-only; mutation-job=approval-gated
```

Expected handoff:

```text
offline=pass; live-auth=separate; graphql-errors=checked; secrets=redacted
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
