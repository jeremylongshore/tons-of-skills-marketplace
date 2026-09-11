---
name: linear-core-workflow-a
description: >-
  Implement a controlled Linear issue lifecycle from discovery through create, update, relation, comment, and archive actions. Use when automating issue operations with the GraphQL API or TypeScript SDK. Trigger with "automate Linear issues", "build an issue workflow", or "update Linear issue states".
argument-hint: "[repository-path] [team-key] [dry-run|apply]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- issue-workflow
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Issue Lifecycle Workflow

## Overview

Build an issue workflow that resolves workspace-owned identifiers first and treats each write as a reviewable, reversible business action.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- `issueCreate` requires a team ID; without a state ID Linear selects the team's first Backlog state, or Triage when enabled.
- The SDK uses verb-first mutation names such as `createIssue`, `updateIssue`, and `archiveIssue`.
- Changes made during the first three minutes after issue creation are treated as part of creation and do not produce activity-log entries.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Resolve the authenticated viewer, organization, target team, workflow states, labels, and assignees using read-only queries.
2. Translate the requested business transition into an explicit create/update/comment/relation plan with stable IDs.
3. Validate required fields, visibility, duplicate policy, and whether Triage changes the default initial state.
4. Preview the exact mutation variables with sensitive or personal fields redacted.
5. After approval, perform one mutation and verify both GraphQL errors and payload success before the next action.
6. Return identifiers, resulting state, reconciliation query, and rollback or archive instructions.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| Team or state not found | Stop and list visible candidates; never fall back to the first team silently. |
| Duplicate issue | Reconcile by an approved external key or canonical URL before creating. |
| Partial mutation response | Treat any GraphQL error as unresolved and verify the issue by ID. |
| Rollback requested | Prefer a documented compensating update or archive; do not delete history casually. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
team=ENG; action=create; title=redacted-summary; mode=dry-run
```

Expected handoff:

```text
team-id=resolved; mutation=issueCreate; approval=pending; rollback=archive
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
