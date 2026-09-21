---
name: quicknode-cost-tuning
description: 'Attribute and reduce QuickNode API-credit consumption by product, endpoint, method, chain, tag, and workload while preserving correctness. Use when forecasting a billing cycle, investigating an overage, or evaluating a caching or data-access change. Trigger with: "reduce QuickNode cost", "analyze QuickNode credits", "find expensive RPC methods".'
allowed-tools: Read, Grep, Write, Edit, Bash(qn:*)
version: 2.0.0
argument-hint: '[billing-window-and-workload]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - quicknode
  - cost
  - api-credits
  - finops
compatibility: 'Credit formulas, product inclusion, and prices are plan-specific and must be read from current account data'
---

# QuickNode Credit and Cost Control

## Overview

Optimize measured API credits, not a guessed requests-per-dollar formula. Account billing periods and endpoint rolling metrics answer different questions, and Streams, Webhooks, SQL, and endpoints can have different consumption models.

## Prerequisites

- Billing window, plan, budget, and workload owner
- Access to Usage & Billing or authorized usage reads
- Product, endpoint, method, chain, and environment tags

## Instructions

### Step 1: Define the denominator

Use Read and Grep to identify workloads, schedules, duplicate callers, cache policy, backfills, and high-cardinality queries. State whether the decision concerns the billing cycle or a rolling performance window.

### Step 2: Retrieve usage

Use Bash(qn:*) for authenticated usage and billing reads. Break consumption down by product and, where supported, endpoint, method, chain, or tag. Do not print invoices or account details into public logs.

### Step 3: Attribute value

Map each large credit consumer to a product outcome and owner. Separate necessary live reads, historical backfills, retries, failed calls, polling, and abandoned experiments.

### Step 4: Choose a safe lever

Use Write or Edit to cache immutable results, replace polling with an event product when justified, bound historical ranges, use pagination and selective fields, or schedule backfills. Never trade correctness for a lower request count silently.

### Step 5: Model the change

Apply the account's current credit and pricing facts to measured volumes. Include plan limits, add-ons, flat-rate endpoints, and private terms only when verified; do not publish confidential pricing.

### Step 6: Verify one billing interval

Compare expected and actual credits, errors, latency, freshness, and business completeness. Alert on both budget burn and missing work so a broken integration cannot look “cheap.”

## Tool Discipline

Use Read and Grep for demand discovery, Bash(qn:*) for read-only account usage, and Write/Edit for controlled optimizations. Plan changes, endpoint pauses, and add-on changes require an owner checkpoint.

## Output

- Credit attribution by product and owner
- Verified plan and billing assumptions
- One correctness-preserving optimization
- Forecast, acceptance metric, and rollback threshold

## Examples

A nightly job repeatedly scans the same historical range. It persists a verified cursor and bounded overlap, reducing credits while retaining reorg reconciliation.

## Error Handling

| Failure | Response |
| --- | --- |
| Usage cannot be segmented | Add endpoint tags or application attribution before optimizing |
| Credit estimate differs from bill | Reconcile billing window, product, add-ons, and private terms |
| Cache returns stale mutable data | Narrow cache scope to immutable or final data |
| Spend drops with missing events | Roll back and restore completeness before further tuning |

## Resources

- [Cost evidence and source notes](references/official-docs.md)
- [QuickNode dashboard usage and billing](https://www.quicknode.com/guides/quicknode-products/how-to-use-the-quicknode-dashboard)
- [Admin API usage](https://www.quicknode.com/docs/admin-api)
