---
name: linktree-security-basics
description: 'Establish a Linktree security baseline for account access, Workspaces, destinations, audience data, and incident response. Use when hardening or reviewing a profile. Trigger with "secure Linktree".'
argument-hint: "[workspace] [profile]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linktree
- security
- mfa
- data-protection
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Linktree account and approval from the profile, Workspace, data, or partner-integration owner
---
# Linktree Account and Data Security Baseline

## Overview

Reduce account takeover, malicious-link, overprivilege, and audience-data risks with documented controls and named owners. Produce a reproducible baseline that makes exceptions and remediation accountability visible.

## Prerequisites

- An authorized Linktree account or a clearly bounded design-only task
- The profile, Workspace, destination, campaign, data, or integration owner appropriate to the requested change
- Current account evidence for plan-dependent features and user-supplied approved partner documentation for every private interface

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository specifications, sanitized fixtures, policies, tests, and prior receipts.

Use `WebFetch` only for current official Linktree documentation or explicitly approved partner documentation.

Use `Write` or `Edit` only after confirming scope, target, owners, data classification, and approval state. These tools do not confer Linktree access, account authority, or permission to process visitor data. Return exact operator steps or an approval-gated handoff when a live action is not authorized.

## Current Contract

- Linktree documents MFA and new-login notifications as account-security controls.
- Workspaces and Admin users create access relationships that require lifecycle ownership.
- Audience, analytics, and destination systems can introduce personal-data and third-party risk beyond the profile itself.

## Authentication

For Admin work, use only the operator's individually provisioned Linktree account, documented Workspace role, and enabled MFA. Never request passwords, one-time codes, browser cookies, recovery codes, or session material. For partner automation, use only the authentication method, environment, scope, storage, rotation, and revocation process in the user-supplied approved partner contract. Public help pages do not establish a general API credential.

## Instructions

1. Identify account and Workspace owners, editors, recovery contacts, connected services, destination owners, data exports, and incident responders.
2. Use Read, Glob, and Grep to inspect access policy, approved destination list, integration inventory, retention rules, and prior incidents without reading secret values.
3. Verify individual accounts, least privilege, MFA, recovery ownership, new-login alert routing, and a tested offboarding process.
4. Review every live destination for approved ownership, HTTPS, expected redirect behavior, and removal procedure; quarantine unexplained links.
5. Minimize audience exports and third-party integrations; document consent, purpose, storage, retention, deletion, and breach escalation.
6. Use Write or Edit to record a redacted control matrix, exceptions, evidence dates, and remediation owners.
7. Use WebFetch only for current official Linktree security, privacy, Workspace, or login guidance.

## Approval Boundaries

Do not share accounts, publish secrets, retain unnecessary subscriber data, or silently accept an unknown destination or administrator.

## Output

Return asset inventory, access and MFA state, destination findings, integration and data-flow findings, exceptions, remediation owners, evidence dates, and risk decision.

## Error Handling

| Condition | Response |
|---|---|
| Unknown administrator exists | Remove or suspend access through the owner-approved process and investigate. |
| Login notification is unexplained | Treat it as a possible incident, rotate access safely, and review sessions. |
| Audience data has no retention rule | Stop new exports until purpose and deletion are approved. |

## Example

The example is a synthetic, redacted operator receipt, not proof of Linktree access or a live account change.

```text
workspace=main; users=4; mfa=4/4; unknown-admins=0; destinations=12-approved; exports=1-controlled; exceptions=0; risk=accepted
```

## Resources

- [Official documentation map](references/official-docs.md) — dated evidence and limits for this workflow.

Read the map before acting. Recheck current account and partner-specific evidence for plan-dependent or private behavior.

## Next Steps

Revalidate source dates, owner approval, target profile, and rollback readiness before repeating the workflow in another account, Workspace, campaign, region, plan, or integration.
