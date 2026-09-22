---
name: clickup-enterprise-rbac
description: >-
  Assess and change ClickUp roles, custom roles, groups, object ACLs, and audit access with plan-aware approvals. Use when governing enterprise ClickUp authorization. Trigger with "ClickUp RBAC", "ClickUp custom roles", or "ClickUp ACL audit".
argument-hint: "[workspace-id] [assess|plan|apply]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- access-control
model: inherit
effort: high
compatibility: Designed for Claude Code; enterprise endpoints require the relevant plan, owner authority, and approved identities
---
# ClickUp Enterprise Access Governance

## Overview

Use API role and ACL evidence as inputs to authorization decisions without assuming a numeric role alone proves effective access.

## Prerequisites

- An Enterprise-plan and owner/admin capability check for the intended endpoint
- An authorized Workspace inventory of users, guests, groups, custom roles, and protected objects
- A ticketed desired-state change with separation of duties and rollback

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- The v2 member `role` field uses 1 owner, 2 admin, 3 member, and 4 guest; custom roles require their own endpoint.
- Groups are user groups, while v2 `team_id` means Workspace.
- User/guest management is Enterprise-only; v3 audit-log queries are Enterprise-only and owner-only.
- v3 ACL changes can alter privacy and sharing and may incur charges; effective access can inherit from hierarchy.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Identify the Workspace, plan, caller role, endpoint version, and approved authorization objective.
2. Inventory direct and inherited access, groups, custom roles, guests, and application tokens.
3. Compare effective access to policy; do not collapse custom roles into the four base role codes.
4. Build a least-privilege plan with additions, removals, charge impact, and rollback.
5. Require a second reviewer for owner/admin, guest, group, or ACL changes; apply bounded changes.
6. Re-read effective access and, where authorized, query audit evidence for the change.

## Approval Boundaries

Never self-approve privilege elevation, owner/admin changes, broad sharing, guest expansion, paid ACL effects, or user removal.

## Output

Return plan/endpoint eligibility, before/after access matrix, inherited-access caveats, approvals, applied changes, audit evidence, and rollback.

## Error Handling

| Condition | Response |
|---|---|
| Plan or owner prerequisite fails | Stop and report the unavailable control. |
| Effective access is ambiguous | Do not remove or grant access until inheritance is resolved. |
| Change would incur unapproved charges | Leave ACLs unchanged. |
| Verification differs from desired state | Roll back safe changes and escalate. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
mode=plan; workspace=approved; custom-roles=3; excessive-access=2; changes=0; second-review=pending
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Object and location ACLs](https://developer.clickup.com/reference/publicpatchacl)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
