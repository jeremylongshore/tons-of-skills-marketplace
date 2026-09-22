---
name: firecrawl-cost-tuning
description: >-
  Measure and reduce Firecrawl credit consumption using explicit limits, endpoint selection, cache policy, format discipline, and spend controls. Use when forecasting or correcting Firecrawl spend. Trigger with "Firecrawl costs", "reduce Firecrawl credits", or "Firecrawl budget".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <budget-window>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, cost, governance]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Credit and Spend Control

## Overview

Optimize against measured business value rather than assumed one-credit requests. Endpoint and option costs differ, modifiers can stack, and crawl or batch charges arrive as pages complete.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Use the current billing page and Credit Usage APIs as the pricing authority. Base scrape/crawl page costs, search/result charges, JSON or other format modifiers, ZDR, parse behavior, Interact minutes, and lockdown outcomes can differ. Polling status does not itself consume credits, while asynchronous page processing can make usage appear later.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Capture the current billing policy, plan, pay-as-you-go state, per-key spend limits, monthly cap, and a baseline by operation and workload class.
2. Attribute usage to an owner, environment, source policy, endpoint, requested formats, page counts, cache behavior, and success category. Never estimate solely from request count.
3. Set explicit crawl and batch bounds. Use map plus selective retrieval when discovery is cheaper than collecting every page.
4. Request only required formats and expensive options. Validate whether JSON extraction, prompt-injection checks, PDF parsing, ZDR, audio/video, or browser interaction earns its added cost.
5. Use maxAge and cache policy only when the freshness SLA permits it; use storeInCache false or ZDR when retention requirements outweigh savings.
6. Add preflight budget checks, alert thresholds, per-key controls where available, and a fail-closed response when the approved ceiling is reached.
7. Run a bounded canary, compare quality-adjusted cost with the baseline, and roll back if savings reduce completeness or violate policy.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before enabling or raising pay-as-you-go, changing plan, increasing a per-key spend limit, trading retention for cache savings, or reducing required quality.

## Output

Return the billing-policy snapshot, workload attribution, baseline and candidate cost, quality delta, chosen controls, alerts, canary evidence, projected range, and rollback threshold.

## Error Handling

- Usage lags async work: wait for job completion and billing settlement before declaring savings.
- Current prices or limits cannot be verified: report a range and block irreversible plan decisions.
- Budget is exhausted: stop new work; do not hide 402 responses with uncontrolled retries.

## Examples

- "Why did credits spike?" attributes usage by option and completed page rather than request count.
- "Make this crawl cheaper" tests scope, cache, format, and map-first changes against quality.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
