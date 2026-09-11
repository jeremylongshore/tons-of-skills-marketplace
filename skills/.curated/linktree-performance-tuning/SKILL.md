---
name: linktree-performance-tuning
description: 'Improve a Linktree visitor path with destination, mobile, content-order, and Insights evidence. Use when a profile is slow, confusing, or underperforming. Trigger with "optimize Linktree performance".'
argument-hint: "[profile-url] [goal]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linktree
- performance
- conversion
- mobile-qa
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Linktree account and approval from the profile, Workspace, data, or partner-integration owner
---
# Linktree Visitor-Path Performance Study

## Overview

Optimize the complete visitor path rather than a fictional API: profile render, content hierarchy, link choice, redirect chain, destination experience, and measured outcome.

## Prerequisites

- An authorized Linktree account or a clearly bounded design-only task
- The profile, Workspace, destination, campaign, data, or integration owner appropriate to the requested change
- Current account evidence for plan-dependent features and user-supplied approved partner documentation for every private interface

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository specifications, sanitized fixtures, policies, tests, and prior receipts.

Use `WebFetch` only for current official Linktree documentation or explicitly approved partner documentation.

Use `Write` or `Edit` only after confirming scope, target, owners, data classification, and approval state. These tools do not confer Linktree access, account authority, or permission to process visitor data. Return exact operator steps or an approval-gated handoff when a live action is not authorized.

## Current Contract

- Linktree recommends considering visitor journey, content order, and focused link sets in its link guidance.
- Insights exposes views, clicks, click rate, sources, and plan-dependent detail for measurement.
- Destination latency and behavior belong to the destination owner and must be measured separately from Linktree.

## Authentication

For Admin work, use only the operator's individually provisioned Linktree account, documented Workspace role, and enabled MFA. Never request passwords, one-time codes, browser cookies, recovery codes, or session material. For partner automation, use only the authentication method, environment, scope, storage, rotation, and revocation process in the user-supplied approved partner contract. Public help pages do not establish a general API credential.

## Instructions

1. Define the visitor goal, target segment, profile, priority link, baseline window, primary metric, guardrail, owner, and rollback threshold.
2. Use Read, Glob, and Grep to inspect the current content inventory, destination owners, campaign history, and prior Insights decisions.
3. Test signed-out mobile and desktop paths, recording visible hierarchy, broken assets, redirect hops, destination readiness, accessibility blockers, and confusing labels.
4. Use the documented Insights definitions and comparable windows to locate drop-off signals without asserting causation.
5. Choose one reversible change to title, order, link type, destination, or profile presentation; keep other variables stable.
6. Use Write or Edit to record the hypothesis, exact change, baseline, review window, result, and rollback decision.
7. Use WebFetch only for current official Linktree link, design, Insights, or sharing guidance.

## Approval Boundaries

Do not use deceptive copy, hide material destination terms, run an uncontrolled multivariable test, or treat personal data as a performance metric.

## Output

Return goal, baseline, path observations, destination findings, hypothesis, one change, primary and guardrail metrics, review window, and rollback threshold.

## Error Handling

| Condition | Response |
|---|---|
| Destination is the bottleneck | Assign remediation to its owner before rearranging the profile. |
| Baseline includes a major campaign | Choose a comparable window or explicitly model the confounder. |
| Change harms accessibility or trust | Roll it back regardless of click lift. |

## Example

The example is a synthetic, redacted operator receipt, not proof of Linktree access or a live account change.

```text
goal=newsletter; baseline=28d; mobile-path=pass; redirect-hops=1; issue=ambiguous-title; change=title-only; metric=unique-clicks; guardrail=unsubscribe-rate
```

## Resources

- [Official documentation map](references/official-docs.md) — dated evidence and limits for this workflow.

Read the map before acting. Recheck current account and partner-specific evidence for plan-dependent or private behavior.

## Next Steps

Revalidate source dates, owner approval, target profile, and rollback readiness before repeating the workflow in another account, Workspace, campaign, region, plan, or integration.
