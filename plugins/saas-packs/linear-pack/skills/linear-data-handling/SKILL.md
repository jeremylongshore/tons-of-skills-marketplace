---
name: linear-data-handling
description: >-
  Classify, minimize, export, retain, and delete Linear-derived data with workspace visibility intact. Use when handling issue content, comments, attachments, audit records, exports, or analytics copies. Trigger with "handle Linear data safely", "export Linear records", or "set Linear retention".
argument-hint: "[repository-path] [data-flow-or-export]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- data-governance
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Data Handling and Export Safety

## Overview

Preserve Linear's team and workspace access boundaries when data leaves the product, and minimize replicated content to the stated purpose.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- Images and other assets may require authentication; external displays should download and self-host approved assets instead of leaking authenticated URLs.
- Workspace CSV exports are admin-controlled, owner-only on Enterprise, recorded in the audit log, and delivered through a link that expires after 12 hours.
- Issue-view CSV limits and role permissions differ; attachment files are not included even when links appear in descriptions.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Inventory data classes, sources, destinations, fields, team visibility, recipients, retention, and deletion owners.
2. Select the least-privileged export path: narrow GraphQL query, approved view export, workspace export, or supported reporting integration.
3. Remove unneeded descriptions, comments, customer requests, emails, attachment links, and audit metadata before transfer.
4. Encrypt approved transfers and stores, bind access to the original team/workspace visibility, and log export authorization.
5. Test deletion, subject-request, legal-hold, and access-revocation behavior on representative synthetic records.
6. Return a field-level data map and evidence without embedding the exported data itself.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| Visibility cannot be preserved | Stop the export or split it by enforceable access boundary. |
| Attachment URL needs auth | Use an approved download/self-host flow; never forward the credential. |
| Export link expired | Request a new owner-approved export instead of weakening controls. |
| Deletion conflicts with hold | Escalate to the data owner and preserve the hold. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
scope=public-team issues; fields=id,title,status; destination=approved-warehouse
```

Expected handoff:

```text
minimum-fields=3; attachments=excluded; access=team-scoped; retention=owner-set
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
