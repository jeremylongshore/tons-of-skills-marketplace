---
name: linktree-install-auth
description: 'Establish Linktree account, workspace, role, MFA, and recovery readiness without fabricating developer credentials. Use when onboarding an operator or integration owner. Trigger with "set up Linktree access".'
argument-hint: "[workspace] [operator-role]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linktree
- access
- mfa
- workspaces
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Linktree account and approval from the profile, Workspace, data, or partner-integration owner
---
# Linktree Account and Access Readiness

## Overview

Create an evidence-backed access plan for a Linktree profile or Workspace, keeping human Admin access separate from any approved partner integration credentials.

## Prerequisites

- An authorized Linktree account or a clearly bounded design-only task
- The profile, Workspace, destination, campaign, data, or integration owner appropriate to the requested change
- Current account evidence for plan-dependent features and user-supplied approved partner documentation for every private interface

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository specifications, sanitized fixtures, policies, tests, and prior receipts.

Use `WebFetch` only for current official Linktree documentation or explicitly approved partner documentation.

Use `Write` or `Edit` only after confirming scope, target, owners, data classification, and approval state. These tools do not confer Linktree access, account authority, or permission to process visitor data. Return exact operator steps or an approval-gated handoff when a live action is not authorized.

## Current Contract

- Linktree documents MFA through SMS in listed regions or an authenticator application.
- Workspaces are the documented surface for managing Linktrees and team access; available controls can vary by plan.
- Developer access is program-gated, so a Linktree login is not evidence of an automation credential or API grant.

## Authentication

For Admin work, use only the operator's individually provisioned Linktree account, documented Workspace role, and enabled MFA. Never request passwords, one-time codes, browser cookies, recovery codes, or session material. For partner automation, use only the authentication method, environment, scope, storage, rotation, and revocation process in the user-supplied approved partner contract. Public help pages do not establish a general API credential.

## Instructions

1. Identify the profile owner, Workspace, requested duties, approver, recovery contact, and offboarding owner.
2. Use Read, Glob, and Grep to inspect local access policy, role matrix, and existing integration inventory without opening secrets.
3. Choose the least-privileged documented Workspace role that satisfies the duties; avoid shared accounts.
4. Enable and verify an available MFA method, record recovery ownership, and confirm new-login notifications reach the accountable owner.
5. If partner automation is requested, require the approved partner agreement, credential issuance record, environment, scopes, rotation path, and revocation test before design work.
6. Use Write or Edit to record the access decision and a redacted joiner/mover/leaver receipt.
7. Use WebFetch only to verify current official Linktree account, Workspace, MFA, or developer-program guidance.

## Approval Boundaries

Do not invite a user, change ownership, weaken MFA, or issue partner credentials until the named account or Workspace owner approves the role and recovery plan.

## Output

Return account class, Workspace, role, MFA state, recovery owner, partner-contract state, revocation test, unresolved access gaps, and approval decision.

## Error Handling

| Condition | Response |
|---|---|
| MFA cannot be enabled | Do not treat password-only access as production-ready; escalate with the account owner. |
| Requested role is broader than duties | Reduce the role or document an explicit, time-bounded exception. |
| API access is assumed from an Admin login | Reject the assumption and obtain partner-program evidence. |

## Example

The example is a synthetic, redacted operator receipt, not proof of Linktree access or a live account change.

```text
workspace=brand-main; role=editor; mfa=authenticator-verified; recovery=security-owner; partner-contract=none; revocation=tested; decision=ready
```

## Resources

- [Official documentation map](references/official-docs.md) — dated evidence and limits for this workflow.

Read the map before acting. Recheck current account and partner-specific evidence for plan-dependent or private behavior.

## Next Steps

Revalidate source dates, owner approval, target profile, and rollback readiness before repeating the workflow in another account, Workspace, campaign, region, plan, or integration.
