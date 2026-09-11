---
name: linktree-core-workflow-a
description: 'Manage the planning, staging, publication, verification, and rollback of a Linktree campaign link using documented Admin controls. Use when shipping a time-bound campaign or content launch. Trigger with "publish Linktree campaign".'
argument-hint: "[profile] [campaign-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linktree
- campaign
- change-control
- publishing
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Linktree account and approval from the profile, Workspace, data, or partner-integration owner
---
# Linktree Governed Campaign Publish

## Overview

Turn campaign intent into a controlled profile change with a destination owner, content review, placement rationale, schedule, acceptance checks, and rollback receipt.

## Prerequisites

- An authorized Linktree account or a clearly bounded design-only task
- The profile, Workspace, destination, campaign, data, or integration owner appropriate to the requested change
- Current account evidence for plan-dependent features and user-supplied approved partner documentation for every private interface

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository specifications, sanitized fixtures, policies, tests, and prior receipts.

Use `WebFetch` only for current official Linktree documentation or explicitly approved partner documentation.

Use `Write` or `Edit` only after confirming scope, target, owners, data classification, and approval state. These tools do not confer Linktree access, account authority, or permission to process visitor data. Return exact operator steps or an approval-gated handoff when a live action is not authorized.

## Current Contract

- Classic links and Link Apps have different visitor behavior and must be selected intentionally.
- Link ordering affects prominence, and Linktree documents scheduled links for time-bound availability.
- Public help guidance supports Admin operations, not an undocumented bulk-publish API.

## Authentication

For Admin work, use only the operator's individually provisioned Linktree account, documented Workspace role, and enabled MFA. Never request passwords, one-time codes, browser cookies, recovery codes, or session material. For partner automation, use only the authentication method, environment, scope, storage, rotation, and revocation process in the user-supplied approved partner contract. Public help pages do not establish a general API credential.

## Instructions

1. Capture campaign owner, audience, approved copy, destination, link type, start and end time, timezone, placement, and rollback trigger.
2. Use Read, Glob, and Grep to compare the campaign brief with the local destination registry and prior change receipts.
3. Validate the destination for HTTPS, expected host, consent and checkout behavior, accessibility, and mobile layout before changing Linktree.
4. Stage the link disabled or scheduled when the account supports it; obtain content and profile-owner approval on the exact preview.
5. Publish in the approved window, confirm order and public rendering, and test the destination without submitting real personal or payment data.
6. Use Write or Edit to record timestamps, operator, approval, evidence, and the exact rollback action.
7. Use WebFetch only for current official instructions on links, ordering, scheduling, or sharing.

## Approval Boundaries

Do not publish early, silently replace a destination, or use a production checkout during verification. A schedule is not a substitute for human approval.

## Output

Return campaign, profile, link type, schedule and timezone, placement, destination checks, approvals, public verification, rollback trigger, and final state.

## Error Handling

| Condition | Response |
|---|---|
| Schedule timezone is ambiguous | Hold publication until the owner confirms an absolute time and timezone. |
| Destination changes after approval | Invalidate the approval and repeat destination review. |
| Rollback cannot be demonstrated | Do not publish until disable or removal is tested safely. |

## Example

The example is a synthetic, redacted operator receipt, not proof of Linktree access or a live account change.

```text
campaign=fall-launch; type=classic; window=approved-UTC; placement=2; mobile=pass; owner-approval=recorded; rollback=disable-link; state=live
```

## Resources

- [Official documentation map](references/official-docs.md) — dated evidence and limits for this workflow.

Read the map before acting. Recheck current account and partner-specific evidence for plan-dependent or private behavior.

## Next Steps

Revalidate source dates, owner approval, target profile, and rollback readiness before repeating the workflow in another account, Workspace, campaign, region, plan, or integration.
