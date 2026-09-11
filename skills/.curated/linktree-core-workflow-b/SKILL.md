---
name: linktree-core-workflow-b
description: 'Turn documented Linktree Insights into a bounded content decision with comparable windows and a reversible experiment. Use when reviewing campaign performance. Trigger with "analyze Linktree Insights".'
argument-hint: "[profile] [date-range]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linktree
- insights
- experiments
- reporting
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Linktree account and approval from the profile, Workspace, data, or partner-integration owner
---
# Linktree Insights Decision Loop

## Overview

Review views, clicks, click rate, sources, and individual-link performance without conflating correlation with attribution or manufacturing unavailable data.

## Prerequisites

- An authorized Linktree account or a clearly bounded design-only task
- The profile, Workspace, destination, campaign, data, or integration owner appropriate to the requested change
- Current account evidence for plan-dependent features and user-supplied approved partner documentation for every private interface

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository specifications, sanitized fixtures, policies, tests, and prior receipts.

Use `WebFetch` only for current official Linktree documentation or explicitly approved partner documentation.

Use `Write` or `Edit` only after confirming scope, target, owners, data classification, and approval state. These tools do not confer Linktree access, account authority, or permission to process visitor data. Return exact operator steps or an approval-gated handoff when a live action is not authorized.

## Current Contract

- Linktree defines total and unique views and clicks, click rate, subscribers, and sources in its Insights documentation.
- History, filters, visitor detail, and CSV exports vary by plan and feature availability.
- Linktree notes that an operator's own test clicks are included and may take time to appear.

## Authentication

For Admin work, use only the operator's individually provisioned Linktree account, documented Workspace role, and enabled MFA. Never request passwords, one-time codes, browser cookies, recovery codes, or session material. For partner automation, use only the authentication method, environment, scope, storage, rotation, and revocation process in the user-supplied approved partner contract. Public help pages do not establish a general API credential.

## Instructions

1. State the decision question, owner, primary metric, guardrail metric, comparison windows, campaign changes, and minimum useful observation period.
2. Use Read, Glob, and Grep to inspect the campaign log, prior baseline, and measurement plan before viewing results.
3. In Insights, set the documented date range and record definitions, plan limitations, visible filters, and any test traffic contamination.
4. Compare equivalent windows and inspect individual-link results and traffic sources; flag launches, outages, or promotions that make them non-comparable.
5. Choose one reversible content, order, title, or promotion experiment; define success and rollback before applying it.
6. Use Write or Edit to save a redacted decision receipt and raw-export provenance when an authorized CSV is available.
7. Use WebFetch only to verify current official metric definitions, export availability, or plan constraints.

## Approval Boundaries

Do not identify visitors, infer causation from a simple before/after change, or upload audience exports to unapproved tools.

## Output

Return decision question, date ranges, metric definitions, plan limitations, observations, confounders, chosen experiment, success threshold, and review date.

## Error Handling

| Condition | Response |
|---|---|
| Windows are not comparable | Report the mismatch and collect a valid baseline instead of forcing a conclusion. |
| CSV is unavailable on the plan | Use the documented on-screen aggregates and record that limitation. |
| Metric definition is unclear | Pause interpretation and verify the current official definition. |

## Example

The example is a synthetic, redacted operator receipt, not proof of Linktree access or a live account change.

```text
question=promote-newsletter; windows=14d-vs-14d; metric=unique-clicks; test-traffic=noted; confounder=launch-day; action=title-test; review=7d
```

## Resources

- [Official documentation map](references/official-docs.md) — dated evidence and limits for this workflow.

Read the map before acting. Recheck current account and partner-specific evidence for plan-dependent or private behavior.

## Next Steps

Revalidate source dates, owner approval, target profile, and rollback readiness before repeating the workflow in another account, Workspace, campaign, region, plan, or integration.
