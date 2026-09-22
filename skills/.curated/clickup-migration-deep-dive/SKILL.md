---
name: clickup-migration-deep-dive
description: >-
  Plan and execute resumable migrations into or between ClickUp Workspaces with explicit mapping, stable source IDs, bounded writes, and reconciliation. Use when moving Jira, Asana, Trello, or ClickUp data. Trigger with "migrate to ClickUp", "ClickUp migration", or "clone ClickUp Workspace".
argument-hint: "[source-system] [destination-workspace-id] [dry-run|pilot|apply]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- migration
model: inherit
effort: high
compatibility: Designed for Claude Code; apply mode requires authorized source/destination access and migration-owner approval
---
# ClickUp Migration and Reconciliation

## Overview

Treat migration as a versioned data program rather than a one-shot task-creation loop. Make each batch resumable, reconcilable, and safe to stop.

## Prerequisites

- Source export/API ownership and a destination Workspace/List allow-list
- Approved field, user, status, date, attachment, comment, and dependency mappings
- A durable reconciliation database, pilot cohort, rate budget, and rollback policy

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- Get Tasks returns 100 records per zero-based page; decide explicitly about closed tasks, subtasks, and Tasks in Multiple Lists.
- Task priorities and dates require ClickUp's documented values and millisecond timestamps.
- Custom Field definitions/options must be resolved first; existing task fields use their separate value endpoints.
- ClickUp does not document a general transactional bulk-create endpoint, so partial progress must be durable and resumable.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Inventory source entities, destination hierarchy, volume, sensitivity, identities, and unsupported concepts.
2. Define mapping versions and validate status, assignee, priority, Custom Field, relationship, and attachment rules.
3. Extract with complete pagination and persist immutable source IDs plus content hashes.
4. Run a no-write transform report, then migrate a representative pilot with strict ceilings.
5. Persist every destination ID before dependent writes and retry only idempotent/transient work.
6. Reconcile counts and sampled field hashes; quarantine exceptions and obtain cutover approval.

## Approval Boundaries

Require explicit approval for production cutover, identity reassignment, attachment transfer, private-content expansion, deletion, or rollback that changes user-visible work.

## Output

Return mapping version, extracted/transformed/migrated/skipped/quarantined counts, ID map, reconciliation results, cutover decision, and rollback state. Name every unresolved owner and deadline.

## Error Handling

| Condition | Response |
|---|---|
| Source ID already mapped | Verify the destination hash and resume; do not duplicate. |
| Mapping target is absent | Quarantine the record and update the versioned mapping. |
| Rate limit reached | Checkpoint and resume after the documented reset. |
| Pilot reconciliation fails | Stop before broad migration and correct the transform. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
mode=pilot; source=jira; extracted=50; migrated=47; quarantined=3; duplicates=0; reconcile=94%
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Get Tasks reference](https://developer.clickup.com/reference/gettasks)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
