---
name: linear-deploy-integration
description: >-
  Connect deployment evidence to Linear work without granting the deploy pipeline broad issue-edit authority. Use when linking releases, commits, pull requests, or rollback receipts to Linear issues. Trigger with "link deploys to Linear", "record Linear release evidence", or "update Linear after deployment".
argument-hint: "[repository-path] [deployment-provider] [dry-run|apply]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- deployment
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Deployment Evidence Integration

## Overview

Design deployment-to-work traceability around stable issue identifiers and owner-approved state changes, while preferring native source-control integration where it satisfies the requirement.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- Linear's GraphQL API is the explicit mutation surface; branch names and commit text are conventions, not proof that a deployment occurred.
- OAuth or app-actor access should be scoped to the teams and operations the deployment reporter actually needs.
- Every mutation result must be checked for GraphQL errors and reconciled by issue ID.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Inspect deployment receipts, Linear's source-control integration, identifier conventions, and current issue-transition policy.
2. Choose the native integration, a read-only evidence link, or a custom mutation path based on the actual gap.
3. Resolve issue identifiers from trusted release metadata; reject free-form or ambiguous branch parsing.
4. Preview comments, links, labels, or state changes and separate evidence recording from workflow transition authority.
5. After the deployment system reports final status and approval is present, perform one idempotent update.
6. Re-query the issue and preserve the deployment, mutation, and rollback receipts.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| No stable issue identifier | Record unmatched evidence for review; do not update a guessed issue. |
| Deployment status uncertain | Wait for the provider's final receipt before mutating Linear. |
| Transition not authorized | Attach or return evidence without changing state. |
| Rollback | Record the rollback as a new event; do not erase the original deployment evidence. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
deployment=prod-2026-09-11.4; issue=ENG-123; status=succeeded; transition=approval-required
```

Expected handoff:

```text
evidence-link=planned; state-change=withheld; idempotency=deployment-id
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
