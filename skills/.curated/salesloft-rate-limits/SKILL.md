---
name: salesloft-rate-limits
description: >-
  Analyze and govern Salesloft's team-wide cost budget with exact response headers, deep-page costs, fair scheduling, and bounded retries. Use when preventing or diagnosing 429 responses. Trigger with "Salesloft rate limits", "Salesloft 429", or "Salesloft request budget".
argument-hint: "[repository-path] [team-alias]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- salesloft
- reliability
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Salesloft Team Rate Budget

## Overview

This skill turns Salesloft rate limiting into measured team capacity. It accounts for other integrations and deep-page multipliers rather than treating request count as cost.

## Prerequisites

- A named Salesloft team and integration owner
- Method/path/page inventory and recent response headers
- A shared per-team scheduler or limiter
- Replay-safe handling for any retried operation

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to locate pagers, retry loops, concurrency, and metrics. Use `WebFetch` only to confirm current official limits and endpoint costs. Use `Write` or `Edit` after the budget policy is approved.

## Current Contract

- Salesloft currently documents a default team-wide limit of 600 cost per minute; Salesloft can adjust it by customer or team.
- Endpoint cost defaults to 1 but can change without endpoint deprecation.
- Page 101-150 costs 3, 151-250 costs 8, 251-500 costs 10, and 501+ costs 30.
- Observe `x-ratelimit-endpoint-cost` and `x-ratelimit-remaining-minute` instead of invented per-minute header names.
- Another integration on the same team can consume the shared budget.

## Authentication

Use the existing team-bound Bearer credential. Do not evade a team limit by rotating credentials or applications.

## Instructions

1. Instrument endpoint cost, remaining-minute value, page number, latency, status, and team alias.
2. Build a limiter keyed by team, not only process or credential.
3. Reserve headroom for interactive and recovery traffic.
4. Replace deep scans with endpoint-supported `updated_at` polling and durable cursors.
5. On 429, honor explicit server guidance when present; otherwise use bounded exponential backoff with jitter.
6. Retry reads and application-idempotent operations only; surface exhausted attempts.
7. Alert on sustained high endpoint cost or unexpected shared-budget depletion.

## Approval Boundaries

Do not increase concurrency, request a provider limit adjustment, or replay uncertain writes without measured evidence and owner approval.

## Output

Return team budget, observed header samples, endpoint/page cost distribution, limiter policy, retry bounds, headroom, and before/after measurements.

## Error Handling

| Condition | Response |
|---|---|
| Missing headers | Use conservative scheduling and flag contract verification. |
| Sudden depletion | Correlate API Logs across all team integrations. |
| 429 on write | Reconcile outcome before any retry. |
| Persistent exhaustion | Reduce work and contact Salesloft with evidence if a limit change is justified. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
team=team-42; endpoint-cost=1; remaining-minute=412; page=1; retry=none
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Rate limits](https://developers.salesloft.com/docs/platform/api-basics/rate-limits/)
- [Efficient cursor poller](https://developers.salesloft.com/docs/platform/guides/building-an-efficient-cursor-poller/)
