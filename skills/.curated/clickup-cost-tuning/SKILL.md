---
name: clickup-cost-tuning
description: >-
  Reduce ClickUp integration cost and request load using measured traffic, pagination, cache policy, webhooks, and current plan facts. Use when forecasting or optimizing ClickUp operations. Trigger with "ClickUp cost", "reduce ClickUp requests", or "ClickUp plan sizing".
argument-hint: "[usage-window] [workspace-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- cost-optimization
model: inherit
effort: high
compatibility: Designed for Claude Code; plan and commercial decisions require current account-owner data
---
# ClickUp Integration Cost and Request Tuning

## Overview

Optimize from observed request and feature usage without inventing prices or treating a plan upgrade as the default remedy.

## Prerequisites

- Per-endpoint request counts, latency, 429s, page depth, polling intervals, and cache hit rates
- Current Workspace plan and feature-use facts supplied by an authorized owner
- Freshness objectives and an approved data-retention policy

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- Rate limits are per token and currently vary by Workspace plan.
- Get Tasks returns at most 100 tasks per page; wasteful full scans multiply requests.
- Webhook delivery can replace polling but requires secure, durable event processing.
- Some features and parameters are plan-gated; current commercial price must come from the account owner.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Measure requests by endpoint, token boundary, caller, result size, and business operation.
2. Identify duplicate reads, empty pages, overbroad polling, retry storms, and unnecessary writes.
3. Model pagination, conditional caching, webhook invalidation, and schedule consolidation.
4. Quantify custom-field uses and plan-gated operations separately from API request volume.
5. Compare alternatives against freshness, failure recovery, security, and owner-provided commercial facts.
6. Implement one bounded change and verify request, latency, error, and staleness deltas.

## Approval Boundaries

Do not change a paid plan, reduce required audit/data controls, create broad webhooks, or accept stale work data without owner approval.

## Output

Return baseline and projected request volume, feature-use facts, optimization decisions, measured savings, freshness impact, and residual risk.

## Error Handling

| Condition | Response |
|---|---|
| Pricing or plan facts are stale | Mark the financial estimate incomplete and obtain current account data. |
| Optimization increases staleness | Roll back or tighten invalidation. |
| 429s persist after request reduction | Inspect token sharing and reset headers before considering plan changes. |
| Webhook replacement loses events | Restore polling fallback and repair durable processing. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
window=14d; requests=-38%; p95=-12%; cache-hit=71%; 429=0; freshness-slo=pass; plan-change=no
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [API availability by plan](https://developer.clickup.com/docs/apis-available-by-plan)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
