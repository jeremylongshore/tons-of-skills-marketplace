---
name: clickup-core-workflow-b
description: >-
  Analyze, inventory, and change ClickUp Spaces, Folders, Lists, tags, and views with parent-aware plans and reversible boundaries. Use when managing ClickUp hierarchy through API v2. Trigger with "ClickUp hierarchy", "ClickUp Lists", or "ClickUp views".
argument-hint: "[workspace-id] [inventory|plan|apply]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- hierarchy
model: inherit
effort: high
compatibility: Designed for Claude Code; mutation requires hierarchy administration in the target Workspace
---
# ClickUp Hierarchy and Views

## Overview

Manage structural objects only after resolving their actual parent chain and downstream task impact. Keep discovery, planning, and mutation as separately reviewable phases.

## Prerequisites

- An allow-listed Workspace and authorized hierarchy administrator
- A current inventory of Spaces, optional Folders, Lists, tags, views, and referenced tasks
- A reviewed desired-state plan and rollback or recreation evidence

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- In v2, `team_id` is a Workspace ID; user groups are separate group resources.
- Lists may be folderless under a Space or nested under a Folder, so the parent endpoint matters.
- Views can exist at Workspace, Space, Folder, or List scope; use the matching endpoint.
- Hierarchy deletion can orphan assumptions in integrations even when the API accepts it.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Inventory Workspace, Space, Folder, List, tag, and view IDs with parent relationships.
2. Map every desired change to its exact v2 endpoint and current object version.
3. Check task counts, automations, webhooks, views, and external references affected by the change.
4. Produce a create/update/delete plan with dependency order and rollback evidence.
5. Apply creates before dependent updates; isolate destructive actions behind approval.
6. Re-read the hierarchy and verify names, parents, privacy, views, and downstream references.

## Approval Boundaries

Do not delete or privatize Spaces, Folders, Lists, views, or tags, or move production work across parents, without owner approval and an impact inventory.

## Output

Return the before/after hierarchy graph, planned/applied operations, affected-task counts, unresolved references, and rollback evidence. Record the authorizer and exact Workspace scope.

## Error Handling

| Condition | Response |
|---|---|
| Parent type is ambiguous | Stop and resolve folderless versus Folder-owned List scope. |
| Object has downstream references | Defer deletion until owners approve a migration. |
| Plan gate denies an operation | Record the gate; do not simulate success. |
| Re-read differs from plan | Stop dependent actions and reconcile drift. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
mode=plan; workspace=approved; spaces=4; lists=27; creates=1; updates=2; deletes=0; blockers=1
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [API v2 and v3 terminology](https://developer.clickup.com/docs/general-v2-v3-api)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
