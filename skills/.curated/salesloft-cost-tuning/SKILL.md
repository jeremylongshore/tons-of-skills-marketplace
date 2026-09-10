---
name: salesloft-cost-tuning
description: >-
  Analyze and reduce Salesloft API capacity waste by measuring endpoint cost, deep pagination, redundant polling, cache churn, and retry amplification. Use when a team is exhausting shared API capacity. Trigger with "Salesloft cost tuning", "reduce Salesloft API usage", or "Salesloft capacity waste".
argument-hint: "[repository-path] [team-alias] [time-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- salesloft
- cost-optimization
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Salesloft API Capacity Tuning

## Overview

This skill optimizes rate-budget consumption, not subscription pricing. It uses observed endpoint cost and business value to remove waste without losing records or hiding failures.

## Prerequisites

- Named team, integration, time window, and business owner
- API Logs or application metrics for endpoint, page, status, and rate headers
- Current synchronization and retention requirements
- Baseline reconciliation results

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect polling schedules, page traversal, caches, and retries. Use `WebFetch` only for official Salesloft rate and polling guidance. Use `Write` or `Edit` after an optimization is tied to measured waste.

## Current Contract

- Salesloft currently starts with 600 cost per minute per team, subject to provider adjustment.
- Endpoint cost defaults to 1 but can change; measure `x-ratelimit-endpoint-cost`.
- Page indices above 100 cost more, reaching 30 points at page 501 and later.
- API Logs can group calls by integration, team, endpoint, response code, and rate usage.
- Webhooks do not replace every change feed; Salesloft documents cursor polling as the general incremental pattern.

## Authentication

Use existing approved access to metrics and API Logs. Never create extra credentials to evade the shared team budget.

## Instructions

1. Measure calls and cost by team, integration, method/path, page range, status, and retry reason.
2. Rank waste from deep pages, duplicate pollers, unchanged records, retry loops, and low-value fields.
3. Replace full scans with documented filters and durable `updated_at` cursors where supported.
4. Coordinate schedules across integrations and reserve recovery headroom.
5. Apply one bounded change and compare cost, lag, completeness, and freshness.
6. Keep only improvements that preserve reconciliation and service objectives.
7. Document any provider limit-adjustment request separately from application optimization.

## Approval Boundaries

Do not claim dollar savings from rate-cost points, reduce required retention, drop records, or disable reconciliation without data-owner approval.

## Output

Return baseline cost, ranked waste, proposed changes, expected capacity impact, measured result, correctness evidence, and remaining shared-budget risk.

## Error Handling

| Condition | Response |
|---|---|
| No rate headers | Use API Logs or instrument responses before estimating. |
| Optimization misses records | Roll back and repair cursor or overlap logic. |
| Another integration dominates | Coordinate at the team level with evidence. |
| Cost changes upstream | Update budgets from observed headers and current docs. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
window=24h; cost=180000->62000; completeness=100%; dollar-claim=none
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Rate limits](https://developers.salesloft.com/docs/platform/api-basics/rate-limits/)
- [Salesloft API Logs](https://developers.salesloft.com/docs/platform/guides/api-logs/)
