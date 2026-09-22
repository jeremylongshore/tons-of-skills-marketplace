---
name: linear-hello-world
description: >-
  Prove Linear authentication and workspace visibility with the smallest read-only GraphQL or SDK query. Use when establishing a new integration baseline without creating test issues. Trigger with "test Linear connection", "Linear hello world", or "verify Linear API key".
argument-hint: "[repository-path] [sdk|graphql]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- connectivity
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Read-Only Connectivity Proof

## Overview

Verify endpoint, auth mode, viewer identity, and visible team count without spending the first test on a production write.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- The GraphQL endpoint is `https://api.linear.app/graphql` and supports introspection.
- Personal API keys use `Authorization: <API_KEY>` without `Bearer`; OAuth access tokens use `Authorization: Bearer <ACCESS_TOKEN>`.
- The official TypeScript SDK accepts either `apiKey` or `accessToken` in `LinearClient`.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Inspect the repository runtime, package manager, secret-loading convention, and existing Linear client code.
2. Select personal API key only for owner-controlled scripts or OAuth for applications used by others.
3. Pin a compatible `@linear/sdk` range or construct a minimal GraphQL request using the correct authorization form.
4. Query only viewer ID/display name and a small page of visible team IDs/keys; inspect GraphQL errors.
5. Record SDK version, auth mode, endpoint, status, and counts without logging the token or returned personal content.
6. Leave all create/update/delete operations for a separately approved workflow.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| 401 | Verify secret injection and the auth-header form without printing the credential. |
| Viewer succeeds, teams empty | Check workspace membership and team access; do not create into a fallback team. |
| GraphQL errors with data | Report the error path and treat the proof as incomplete. |
| SDK incompatible | Compare the installed package and Node version with current package metadata. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
runtime=node20; client=sdk; auth=personal-key-reference; operation=viewer+teams(first:5)
```

Expected handoff:

```text
endpoint=verified; viewer=present; visible-teams=count-only; mutations=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
