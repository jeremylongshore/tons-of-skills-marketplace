---
name: linear-core-workflow-b
description: >-
  Coordinate Linear projects, cycles, initiatives, milestones, and issue membership without assuming a workspace taxonomy. Use when implementing portfolio or planning automation. Trigger with "sync Linear project", "manage Linear cycles", or "coordinate Linear initiatives".
argument-hint: "[repository-path] [project-or-cycle] [dry-run|apply]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- planning-workflow
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Project and Cycle Coordination

## Overview

Map planning intent onto the workspace's actual project, cycle, initiative, and team model before making relationship changes.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- Issues belong to one team, while projects can belong to one or more teams; access must be evaluated at both levels.
- List operations are Relay-style connections and must be paginated rather than assuming `nodes` is complete.
- Archived resources are hidden by default and require `includeArchived: true` when reconciliation needs them.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Discover visible teams, project statuses, cycles, initiatives, milestones, and archived-state requirements.
2. Define the source of truth and stable matching keys for every entity; names alone are not sufficient for unattended writes.
3. Build a read-only diff of requested membership, dates, status, and ownership changes.
4. Validate cross-team visibility and reject any mapping that would expose a private team's issues.
5. Apply approved mutations in dependency order and stop on the first GraphQL or payload failure.
6. Re-query every changed entity and produce a reconciliation report with compensating actions.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| Ambiguous name match | Require a stable ID or owner-confirmed mapping. |
| Archived entity missing | Repeat the read with `includeArchived: true` before creating a replacement. |
| Cross-team access gap | Stop; do not infer visibility from project membership. |
| Partial batch | Record successful IDs, halt remaining writes, and reconcile before retrying. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
initiative=Q4; project=Billing; teams=ENG,PLAT; mode=dry-run
```

Expected handoff:

```text
mapping=reviewed; visibility=pass; mutations=0; approval=pending
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
