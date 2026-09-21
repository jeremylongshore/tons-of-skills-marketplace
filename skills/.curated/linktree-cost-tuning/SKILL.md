---
name: linktree-cost-tuning
description: 'Evaluate Linktree plan and feature value from current pricing, actual usage, and documented availability. Use when renewing, upgrading, or reducing spend. Trigger with "review Linktree cost".'
argument-hint: "[workspace] [review-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linktree
- cost
- plans
- value-review
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Linktree account and approval from the profile, Workspace, data, or partner-integration owner
---
# Linktree Plan and Feature Value Review

## Overview

Build a decision-ready plan review based on needed outcomes, active profiles, operator time, Insights history, and audience or commerce requirements rather than static copied prices.

## Prerequisites

- An authorized Linktree account or a clearly bounded design-only task
- The profile, Workspace, destination, campaign, data, or integration owner appropriate to the requested change
- Current account evidence for plan-dependent features and user-supplied approved partner documentation for every private interface

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository specifications, sanitized fixtures, policies, tests, and prior receipts.

Use `WebFetch` only for current official Linktree documentation or explicitly approved partner documentation.

Use `Write` or `Edit` only after confirming scope, target, owners, data classification, and approval state. These tools do not confer Linktree access, account authority, or permission to process visitor data. Return exact operator steps or an approval-gated handoff when a live action is not authorized.

## Current Contract

- Linktree pricing and feature availability can change and must be verified at decision time.
- Insights history, filters, exports, and audience capabilities vary by plan according to current help guidance.
- A feature's presence does not prove incremental value; actual usage and business outcomes are required.

## Authentication

For Admin work, use only the operator's individually provisioned Linktree account, documented Workspace role, and enabled MFA. Never request passwords, one-time codes, browser cookies, recovery codes, or session material. For partner automation, use only the authentication method, environment, scope, storage, rotation, and revocation process in the user-supplied approved partner contract. Public help pages do not establish a general API credential.

## Instructions

1. Define the decision date, billing owner, current plan, profiles and Workspaces, renewal terms, required outcomes, and non-negotiable controls.
2. Use Read, Glob, and Grep to inspect approved invoices, plan inventory, usage receipts, campaign results, and operator-time estimates without exposing payment details.
3. Use WebFetch to capture current official pricing and help evidence on the review date; record region, billing cadence, tax assumptions, and feature caveats.
4. Map each used or requested feature to an owner, frequency, measurable outcome, alternative, and documented plan requirement.
5. Compare keep, upgrade, downgrade, and consolidate scenarios, including migration effort, lost history, access changes, and operational risk.
6. Use Write or Edit to produce a redacted recommendation with sensitivity ranges instead of false precision.
7. Set a follow-up date and measurable trigger for revisiting the decision.

## Approval Boundaries

Do not change a subscription, payment method, Workspace, or data export policy without billing and account-owner approval.

## Output

Return evidence date, current plan, required capabilities, used capabilities, scenario costs, assumptions, migration risks, recommendation, approvers, and next review trigger.

## Error Handling

| Condition | Response |
|---|---|
| Pricing region is unknown | Present a range and obtain the account's actual renewal quote. |
| Feature requirement has no owner | Exclude it from the must-have set until accountability is assigned. |
| Downgrade may remove history or access | Confirm documented impact and export needs before approval. |

## Example

The example is a synthetic, redacted operator receipt, not proof of Linktree access or a live account change.

```text
workspace=brand; evidence-date=2026-09-11; outcomes=3; used-features=5; scenarios=keep|downgrade; recommendation=keep; sensitivity=renewal-quote-pending
```

## Resources

- [Official documentation map](references/official-docs.md) — dated evidence and limits for this workflow.

Read the map before acting. Recheck current account and partner-specific evidence for plan-dependent or private behavior.

## Next Steps

Revalidate source dates, owner approval, target profile, and rollback readiness before repeating the workflow in another account, Workspace, campaign, region, plan, or integration.
