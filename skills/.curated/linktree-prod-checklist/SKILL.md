---
name: linktree-prod-checklist
description: 'Review and gate a Linktree profile, campaign, audience, commerce, or partner-integration change before production. Use when approving a release. Trigger with "Linktree production checklist".'
argument-hint: "[change-id] [profile]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linktree
- production
- release-gate
- change-control
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Linktree account and approval from the profile, Workspace, data, or partner-integration owner
---
# Linktree Production Change Checklist

## Overview

Issue a fail-closed go/no-go decision across ownership, access, content, destinations, data handling, testing, service status, monitoring, and rollback.

## Prerequisites

- An authorized Linktree account or a clearly bounded design-only task
- The profile, Workspace, destination, campaign, data, or integration owner appropriate to the requested change
- Current account evidence for plan-dependent features and user-supplied approved partner documentation for every private interface

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository specifications, sanitized fixtures, policies, tests, and prior receipts.

Use `WebFetch` only for current official Linktree documentation or explicitly approved partner documentation.

Use `Write` or `Edit` only after confirming scope, target, owners, data classification, and approval state. These tools do not confer Linktree access, account authority, or permission to process visitor data. Return exact operator steps or an approval-gated handoff when a live action is not authorized.

## Current Contract

- Linktree features and availability vary by plan, region, and current product state.
- Public UI workflows and private partner automation have different evidence and authorization requirements.
- Audience and commerce changes add privacy, consent, payment, and support responsibilities beyond link publishing.

## Authentication

For Admin work, use only the operator's individually provisioned Linktree account, documented Workspace role, and enabled MFA. Never request passwords, one-time codes, browser cookies, recovery codes, or session material. For partner automation, use only the authentication method, environment, scope, storage, rotation, and revocation process in the user-supplied approved partner contract. Public help pages do not establish a general API credential.

## Instructions

1. Freeze change ID, reviewed revision, target profile and Workspace, operator, approver, window, scope, and excluded changes.
2. Use Read, Glob, and Grep to verify acceptance evidence, destination approvals, access review, synthetic tests, data-impact review, monitoring, and rollback receipt.
3. Confirm required plan and region features on the target account and Linktree service status near the window.
4. Verify signed-out mobile and desktop behavior, accessibility, content approval, destination ownership, schedule timezone, and sharing preview.
5. For audience, commerce, or partner automation, verify consent, terms, data minimization, retention, deletion, private-contract revision, and support ownership.
6. Use Write or Edit to produce a signed checklist with explicit pass, fail, not applicable, and evidence for every item.
7. Use WebFetch only for current official Linktree guidance and status evidence.

## Approval Boundaries

Any missing owner, missing rollback, failed critical check, active material incident, or undocumented private interface is a no-go—not an assumed pass.

## Output

Return change ID, revision, checks by domain, evidence links, exceptions, approvers, monitoring and rollback readiness, blockers, and final go/no-go.

## Error Handling

| Condition | Response |
|---|---|
| Evidence belongs to another revision | Reject it and rerun the affected gate on the frozen revision. |
| Required feature is unavailable | Change scope or plan; do not improvise around the product boundary. |
| Rollback owner is absent | Hold the release until an accountable operator is available. |

## Example

The example is a synthetic, redacted operator receipt, not proof of Linktree access or a live account change.

```text
change=lt-88; revision=def456; access=pass; content=pass; destinations=pass; data=na; status=pass; rollback=pass; decision=go
```

## Resources

- [Official documentation map](references/official-docs.md) — dated evidence and limits for this workflow.

Read the map before acting. Recheck current account and partner-specific evidence for plan-dependent or private behavior.

## Next Steps

Revalidate source dates, owner approval, target profile, and rollback readiness before repeating the workflow in another account, Workspace, campaign, region, plan, or integration.
