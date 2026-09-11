---
name: linktree-common-errors
description: 'Triage common Linktree publishing, login, destination, rendering, and Insights symptoms with bounded evidence. Use when an operator reports a Linktree problem. Trigger with "troubleshoot Linktree".'
argument-hint: "[profile-url] [symptom]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linktree
- troubleshooting
- triage
- operations
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Linktree account and approval from the profile, Workspace, data, or partner-integration owner
---
# Linktree Operator Troubleshooting Triage

## Overview

Classify the failing layer before changing anything: account access, Linktree status, profile configuration, browser rendering, destination system, analytics delay, or private integration.

## Prerequisites

- An authorized Linktree account or a clearly bounded design-only task
- The profile, Workspace, destination, campaign, data, or integration owner appropriate to the requested change
- Current account evidence for plan-dependent features and user-supplied approved partner documentation for every private interface

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository specifications, sanitized fixtures, policies, tests, and prior receipts.

Use `WebFetch` only for current official Linktree documentation or explicitly approved partner documentation.

Use `Write` or `Edit` only after confirming scope, target, owners, data classification, and approval state. These tools do not confer Linktree access, account authority, or permission to process visitor data. Return exact operator steps or an approval-gated handoff when a live action is not authorized.

## Current Contract

- A visible Linktree button and its destination are separate failure domains.
- Linktree documents account-login recovery and states that Insights data may not appear immediately.
- Private partner behavior cannot be diagnosed from invented public response codes or endpoints.

## Authentication

For Admin work, use only the operator's individually provisioned Linktree account, documented Workspace role, and enabled MFA. Never request passwords, one-time codes, browser cookies, recovery codes, or session material. For partner automation, use only the authentication method, environment, scope, storage, rotation, and revocation process in the user-supplied approved partner contract. Public help pages do not establish a general API credential.

## Instructions

1. Capture the exact symptom, profile URL, link title, expected result, first-seen time and timezone, affected audience, device class, and latest approved change.
2. Use Read, Glob, and Grep to inspect change receipts, destination inventory, browser evidence, and sanitized integration logs.
3. Check official service status, then reproduce signed out and distinguish missing or disabled content from a broken external destination.
4. For login symptoms, follow documented recovery and MFA guidance; never request a password, one-time code, or session cookie.
5. For Insights symptoms, verify metric definition, date range, plan availability, test traffic, and documented refresh behavior before declaring data loss.
6. Use Write or Edit to record the classification, evidence, one reversible next action, and escalation owner.
7. Use WebFetch only for current official Linktree status and help guidance.

## Approval Boundaries

Do not change multiple links during diagnosis, collect credentials, or blame Linktree when evidence points to a destination or browser-specific failure.

## Output

Return symptom, failing layer, evidence, status, reproduction matrix, latest change, safe next action, rollback state, escalation owner, and confidence.

## Error Handling

| Condition | Response |
|---|---|
| Failure layer is ambiguous | Freeze changes and gather one discriminating observation at a time. |
| Only signed-in reproduction exists | Repeat signed out before concluding the public experience is affected. |
| Support asks for sensitive data | Provide a redacted minimum or use an approved secure channel. |

## Example

The example is a synthetic, redacted operator receipt, not proof of Linktree access or a live account change.

```text
symptom=blank-destination; layer=external-site; signed-out=yes; devices=2/2; status=operational; latest-change=none; next=destination-owner; confidence=high
```

## Resources

- [Official documentation map](references/official-docs.md) — dated evidence and limits for this workflow.

Read the map before acting. Recheck current account and partner-specific evidence for plan-dependent or private behavior.

## Next Steps

Revalidate source dates, owner approval, target profile, and rollback readiness before repeating the workflow in another account, Workspace, campaign, region, plan, or integration.
