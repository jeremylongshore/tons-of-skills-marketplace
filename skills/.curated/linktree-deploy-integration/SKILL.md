---
name: linktree-deploy-integration
description: 'Roll out an approved Linktree profile or campaign change through preview, bounded publication, verification, and rollback. Use when promoting a tested change. Trigger with "deploy Linktree update".'
argument-hint: "[change-id] [profile]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linktree
- deployment
- rollout
- rollback
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Linktree account and approval from the profile, Workspace, data, or partner-integration owner
---
# Linktree Staged Profile Rollout

## Overview

Coordinate a human-operated or contract-approved rollout with exact scope, evidence, monitoring, and a tested rollback instead of treating the profile as generic application infrastructure.

## Prerequisites

- An authorized Linktree account or a clearly bounded design-only task
- The profile, Workspace, destination, campaign, data, or integration owner appropriate to the requested change
- Current account evidence for plan-dependent features and user-supplied approved partner documentation for every private interface

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository specifications, sanitized fixtures, policies, tests, and prior receipts.

Use `WebFetch` only for current official Linktree documentation or explicitly approved partner documentation.

Use `Write` or `Edit` only after confirming scope, target, owners, data classification, and approval state. These tools do not confer Linktree access, account authority, or permission to process visitor data. Return exact operator steps or an approval-gated handoff when a live action is not authorized.

## Current Contract

- Linktree documents profile editing, scheduled links, sharing, and Insights through its product surfaces.
- Feature and plan availability must be checked on the target account at deployment time.
- Any automated deployment requires an approved partner contract; otherwise use documented Admin controls.

## Authentication

For Admin work, use only the operator's individually provisioned Linktree account, documented Workspace role, and enabled MFA. Never request passwords, one-time codes, browser cookies, recovery codes, or session material. For partner automation, use only the authentication method, environment, scope, storage, rotation, and revocation process in the user-supplied approved partner contract. Public help pages do not establish a general API credential.

## Instructions

1. Freeze the reviewed change ID, profile, operator, approver, release window, expected public state, monitoring window, and rollback trigger.
2. Use Read, Glob, and Grep to verify the reviewed specification, destination evidence, synthetic test result, and prior profile snapshot.
3. Confirm Linktree service status and each destination's owner-approved readiness before the change window.
4. Apply only the reviewed delta through Admin controls or the explicitly approved partner adapter; do not bundle unrelated edits.
5. Verify signed-out mobile and desktop rendering, order, destinations, schedule, and relevant Insights baseline without submitting personal data.
6. Use Write or Edit to record the deployed revision, timestamps, evidence, observations, and rollback status.
7. Use WebFetch only for current official help, status, or approved partner documentation.

## Approval Boundaries

Do not promote an unreviewed delta, continue through a vendor incident, or improvise an automated write path. Roll back when a defined trigger fires.

## Output

Return change ID, profile, reviewed revision, service status, applied delta, public checks, monitoring window, rollback trigger, rollback readiness, and final decision.

## Error Handling

| Condition | Response |
|---|---|
| Profile differs from the reviewed snapshot | Stop, reconcile drift, and obtain a new review. |
| Linktree status shows an active incident | Pause unless the incident owner explicitly accepts the risk. |
| Post-publish destination check fails | Execute the approved rollback and record the exposure. |

## Example

The example is a synthetic, redacted operator receipt, not proof of Linktree access or a live account change.

```text
change=lt-2026-09; revision=abc123; status=operational; delta=1-link; checks=pass; monitor=60m; rollback=ready; decision=hold-monitor
```

## Resources

- [Official documentation map](references/official-docs.md) — dated evidence and limits for this workflow.

Read the map before acting. Recheck current account and partner-specific evidence for plan-dependent or private behavior.

## Next Steps

Revalidate source dates, owner approval, target profile, and rollback readiness before repeating the workflow in another account, Workspace, campaign, region, plan, or integration.
