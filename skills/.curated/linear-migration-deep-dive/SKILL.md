---
name: linear-migration-deep-dive
description: >-
  Plan and execute a controlled migration into Linear using supported import assistants or the CLI importer. Use when moving issues from Jira, GitHub, Asana, Shortcut, another Linear workspace, or CSV. Trigger with "migrate to Linear", "import issues into Linear", or "plan Linear cutover".
argument-hint: "[source-system] [pilot|cutover|reconcile]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- data-migration
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Workspace Data Migration

## Overview

Choose the supported importer that preserves the required data, pilot a bounded team, and prove mappings and rollback before cutover.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- Imports require a workspace admin; dedicated import assistants are preferred because they retain more source data and can support bulk deletion for a limited time.
- The CLI importer is for sources without a dedicated assistant and does not preserve all data such as comments or projects.
- Re-importing the same source into the same team skips already-imported issues unless the prior import is deleted first.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Inventory source entities, volumes, users, teams, statuses, labels, projects, comments, attachments, timestamps, and compliance constraints.
2. Choose a dedicated assistant when available; use the CLI only after documenting the data it cannot preserve.
3. Define deterministic user, team, workflow, priority, estimate, and label mappings plus explicit exclusions.
4. Run a small pilot into an approved destination team and validate counts, samples, permissions, links, and timestamps.
5. Approve the cutover window, source freeze, communications, duplicate policy, rollback window, and accountable owners.
6. After import, reconcile counts and sampled semantics, preserve receipts, and keep the legacy source read-only for the approved period.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| Unsupported field | Record the loss and choose an archive or alternate migration path before cutover. |
| User mapping ambiguous | Require owner-confirmed mapping; do not create or merge identities automatically. |
| Pilot incorrect | Delete the pilot only while the supported option remains and after approval, then repair mappings. |
| Rollback window unknown | Do not cut over until current importer deletion behavior is verified. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
source=jira; teams=2; issues=500; mode=pilot; comments=required
```

Expected handoff:

```text
method=dedicated-assistant; mappings=review; cutover=not-approved
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
