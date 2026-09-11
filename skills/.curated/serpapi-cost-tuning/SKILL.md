---
name: serpapi-cost-tuning
description: 'Reduce SerpAPI search consumption through measured demand, exact-query caching, admission budgets, and current account pricing evidence. Use when forecasting or controlling search spend. Trigger with "optimize SerpAPI cost".'
argument-hint: "[environment] [forecast-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, serpapi, cost, finops, caching]
model: inherit
effort: high
compatibility: Designed for Claude Code; plan changes and production admission/cache changes require finance, product, and account-owner approval
---
# SerpAPI Usage and Cost Governance

## Overview

Forecast from observed search demand and the account's current contract, then reduce waste without inventing static plan economics.

## Prerequisites

- Current pricing page and Account API snapshot
- Search attempts, server/application cache hits, engine mix, retries, and business outcome volume
- Product freshness requirements and owners for finance, product, and the SerpAPI account

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inventory callers, cache behavior, and retry amplification, `WebFetch` to verify current public pricing and cache rules, and `Write` or `Edit` for forecasts, budgets, dashboards, and safe optimizations.

## Current Contract

Plans, prices, included searches, and hourly throughput can change. Account API exposes the subscribed plan, searches left, usage, renewal date, and throughput. Exactly matching cached searches can be served from SerpAPI's one-hour cache for free; `no_cache=true` opts out and can increase consumption.

## Authentication

Read account facts with the server-side `SERPAPI_KEY`, but do not expose the key, account identity, or commercial details in public dashboards or receipts.

## Instructions

1. Enumerate every producer and separate user-valued searches from retries, duplicate requests, tests, previews, and abandoned work.
2. Capture a dated Account API snapshot and current pricing evidence; do not embed public list prices as durable code constants.
3. Forecast searches through the next renewal using observed volume, seasonality, cache hit rate, pagination, and failure amplification.
4. Rank optimizations: remove duplicate calls, normalize exact-match parameters, enable application caching, stop unnecessary pagination, gate low-value work, and eliminate uncontrolled retries.
5. Preserve freshness and correctness requirements; never claim that reducing result count reduces the number of searches without current evidence.
6. Model base, expected, and peak scenarios with headroom and an explicit assumption register.
7. Present product-impacting budgets or plan changes for approval, canary safe changes, and reconcile forecast to actual usage.

## Output

Return dated account/pricing evidence, producer ledger, demand forecast, waste analysis, prioritized controls, scenario assumptions, approval decisions, and forecast-versus-actual owner.

## Error Handling

| Condition | Response |
|---|---|
| Pricing differs from the model | Refresh evidence and invalidate the stale scenario. |
| Usage exceeds events recorded | Audit retries, pagination, hidden producers, and `no_cache`. |
| Cache lowers search quality | Restore the freshness contract and evaluate narrower reuse. |
| Renewal date is absent | Confirm whether the account uses a non-monthly or cancelled arrangement. |

## Example

```text
window=to-renewal; demand=observed; waste=duplicate-plus-retry; pricing=evidence-dated; scenarios=base/expected/peak; headroom=approved; action=normalize-cache-keys
```

## Resources

- [Plans and pricing](https://serpapi.com/pricing)
- [Account API](https://serpapi.com/account-api)
- [Google Search cache behavior](https://serpapi.com/search-api#serpapi-parameters)

## Next Steps

Reconcile the forecast weekly and reopen the plan decision before renewal or a material demand change.
