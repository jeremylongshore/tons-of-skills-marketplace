---
name: linktree-upgrade-migration
description: 'Plan and verify a Linktree plan, profile, Workspace, username, or integration migration with preserved evidence and rollback. Use when account structure changes. Trigger with "migrate Linktree".'
argument-hint: "[migration-id] [change-type]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linktree
- migration
- workspaces
- rollback
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Linktree account and approval from the profile, Workspace, data, or partner-integration owner
---
# Linktree Plan, Profile, and Workspace Migration

## Overview

Inventory current state, classify plan-dependent and externally referenced assets, rehearse the change, and verify public and operator paths without assuming portability.

## Prerequisites

- An authorized Linktree account or a clearly bounded design-only task
- The profile, Workspace, destination, campaign, data, or integration owner appropriate to the requested change
- Current account evidence for plan-dependent features and user-supplied approved partner documentation for every private interface

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository specifications, sanitized fixtures, policies, tests, and prior receipts.

Use `WebFetch` only for current official Linktree documentation or explicitly approved partner documentation.

Use `Write` or `Edit` only after confirming scope, target, owners, data classification, and approval state. These tools do not confer Linktree access, account authority, or permission to process visitor data. Return exact operator steps or an approval-gated handoff when a live action is not authorized.

## Current Contract

- Plan capabilities, analytics history, profiles, and Workspace behavior must be verified against current official guidance and the target account.
- Public profile URLs, QR codes, social bios, campaign materials, and external destinations can create dependencies outside Linktree.
- Private partner integrations require contract-specific migration and credential evidence.

## Authentication

For Admin work, use only the operator's individually provisioned Linktree account, documented Workspace role, and enabled MFA. Never request passwords, one-time codes, browser cookies, recovery codes, or session material. For partner automation, use only the authentication method, environment, scope, storage, rotation, and revocation process in the user-supplied approved partner contract. Public help pages do not establish a general API credential.

## Instructions

1. Define migration type, source and target state, profile and Workspace owners, billing owner, window, success criteria, freeze point, and rollback deadline.
2. Use Read, Glob, and Grep to inventory profiles, live links, schedules, QR assets, social placements, sharing previews, exports, users, integrations, and change history.
3. Use WebFetch to verify current official plan, Workspace, URL, QR, Insights export, and relevant feature behavior on the evidence date.
4. Classify every asset as preserved, recreated, redirected, exported, owner-notified, unsupported, or blocked; minimize personal-data movement.
5. Rehearse with synthetic fixtures and a written sequence, including access loss, stale social bio, broken QR, destination failure, and rollback.
6. Apply only after approval, then verify signed-out public paths, operator access, Insights continuity expectations, billing state, and downstream references.
7. Use Write or Edit to record before and after snapshots, decisions, exceptions, communications, and rollback state.

## Approval Boundaries

Do not assume usernames, custom domains, history, subscribers, plan features, or private integrations transfer. Do not move audience data without approved purpose and controls.

## Output

Return migration ID, source and target, asset disposition table, plan and billing evidence, access checks, public-path checks, data handling, exceptions, rollback deadline, and outcome.

## Error Handling

| Condition | Response |
|---|---|
| A public dependency owner is unknown | Block the cutover or preserve the old path until ownership is resolved. |
| History or export availability is uncertain | Capture approved evidence before changing the plan. |
| Post-migration access is incomplete | Use the rollback or break-glass plan and halt further changes. |

## Example

The example is a synthetic, redacted operator receipt, not proof of Linktree access or a live account change.

```text
migration=workspace-consolidation; profiles=3; assets=27; preserved=24; recreated=3; audience-data=none; public-checks=pass; rollback-until=24h; outcome=complete
```

## Resources

- [Official documentation map](references/official-docs.md) — dated evidence and limits for this workflow.

Read the map before acting. Recheck current account and partner-specific evidence for plan-dependent or private behavior.

## Next Steps

Revalidate source dates, owner approval, target profile, and rollback readiness before repeating the workflow in another account, Workspace, campaign, region, plan, or integration.
