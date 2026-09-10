---
name: clickup-core-workflow-a
description: >-
  Create, reconcile, update, and retire ClickUp tasks with schema validation, durable source identity, and explicit destructive approval. Use when automating task lifecycle work through ClickUp API v2. Trigger with "ClickUp task sync", "create ClickUp tasks", or "ClickUp task CRUD".
argument-hint: "[workspace-id] [list-id] [dry-run|apply]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- tasks
model: inherit
effort: high
compatibility: Designed for Claude Code; apply mode requires authorized ClickUp task access
---
# ClickUp Task Lifecycle

## Overview

Operate the v2 task surface without duplicate creation, silent field loss, or unsafe deletion. Preserve a durable reconciliation trail for every attempted change.

## Prerequisites

- An allow-listed Workspace and destination List with a confirmed status/assignee model
- A personal or OAuth token authorized for the target hierarchy
- A durable external source key, reconciliation store, and rollback policy

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- Task creation uses `POST /api/v2/list/LIST_ID/task`; update and delete use the task resource path.
- Priorities are `1` urgent, `2` high, `3` normal, and `4` low.
- Existing Custom Fields are changed through Set/Remove Custom Field Value, not Update Task.
- Get Tasks returns 100 tasks per zero-based page and normally includes only home-List tasks; request Tasks in Multiple Lists explicitly with `include_timl`.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Read the destination List, statuses, members, and accessible Custom Fields.
2. Normalize source records and validate names, dates in milliseconds, priorities, assignees, and field option IDs.
3. Search the reconciliation store before creating; never assume an undocumented idempotency header.
4. Render a dry-run of creates, updates, Custom Field calls, skips, and proposed removals.
5. Apply bounded writes, persist returned task IDs immediately, and stop on permission or schema drift.
6. Re-read affected tasks and reconcile values, counts, errors, and rollback handles.

## Approval Boundaries

Require explicit approval before deletes, bulk status changes, reassignment, date shifts, cross-List moves, or Custom Field writes that consume plan-limited uses.

## Output

Return dry-run/apply mode, created/updated/skipped/deleted counts, external-to-ClickUp ID map, verification result, and rollback handles. Identify every rejected or quarantined record with its safe remediation.

## Error Handling

| Condition | Response |
|---|---|
| Source key already maps to a task | Update or skip according to policy; do not duplicate. |
| Status or option ID is invalid | Stop that record and refresh destination metadata. |
| Partial write succeeds | Persist the task ID and resume idempotently. |
| Delete is unapproved | Leave the task unchanged and report the proposed action. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
mode=dry-run; list=allow-listed; create=8; update=3; delete=0; custom-field-uses=2; conflicts=1
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Tasks guide](https://developer.clickup.com/docs/tasks)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
