---
name: brightdata-rate-limits
description: 'Analyze and design Bright Data concurrency and backoff controls from observed provider signals and owned budgets instead of invented global limits. Use when handling 429 responses, dataset job ceilings, or uneven proxy pressure. Trigger with: "tune Bright Data concurrency", "handle Bright Data 429", "set a dataset job budget".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: "[workload-profile]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- web-data
- bright-data
- rate-limits
- operations
compatibility: 'Requires an approved Bright Data account or offline fixtures, current Bright Data documentation, and an authorized public-data collection purpose'
---
# Bright Data Adaptive Capacity Control

## Overview

Bright Data does not publish one global proxy request limit. Build separate controllers for proxy traffic and dataset jobs, honor current provider signals, and keep target, cost, and policy ceilings stricter than capacity.

## Prerequisites

- A workload profile with target, product, and idempotency classes
- Observed latency, error, and provider-code samples
- Owner-approved concurrency, byte, cost, and wall-time ceilings

## Instructions

### Step 1: Measure the lane

Read recent receipts and Grep for 429, `Retry-After`, provider error codes, active dataset jobs, per-IP concentration, and queue depth. Do not infer capacity from successful bursts alone.

### Step 2: Separate controllers

Write independent limits for proxy requests, Browser API sessions, async triggers, progress polling, downloads, and delivery workers. One product's success must not raise another product's ceiling.

### Step 3: Apply evidence-based backoff

Retry only idempotent transient work. Honor provider guidance, use bounded jitter, cap attempts and elapsed time, and open the circuit on policy, authentication, or data errors.

### Step 4: Tune gradually

Edit one limit at a time, run an approved canary, compare throughput, error, and cost, and retain the lower limit unless the evidence and owner approve promotion.

## Tool Discipline

Use Read and Grep to analyze redacted metrics and documented codes. Use Write and Edit for controller configuration, tests, and runbooks. This skill does not run live traffic or change Bright Data account limits.

## Output

- Per-lane concurrency and queue budgets
- Retry and circuit matrix by documented failure class
- Canary comparison with rollback threshold

## Examples

If dataset triggers return a tenant-specific parallel-job error, stop launching new jobs and continue bounded progress polling for owned snapshots. If proxy traffic returns a per-IP 429, reduce pressure and review distribution rather than guessing a universal rate.

## Error Handling

| Failure | Meaning | Response |
|---------|---------|----------|
| No provider code is retained | 429 cause is ambiguous | Improve redacted instrumentation before tuning |
| Retries amplify queue depth | Backoff lacks admission control | Open the circuit and drain owned work |
| Throughput improves but cost or error ceiling fails | Optimization violates the budget | Roll back the changed limit |

## Resources

- [Proxy error catalog](https://docs.brightdata.com/proxy-networks/errorCatalog)
- [Scraper async requests guide](https://docs.brightdata.com/products/scrapers/scrapers-library/async-requests)
- [Download snapshot](https://docs.brightdata.com/api-reference/scrapers/delivery-apis/download-snapshot)
- [Proxy configuration options](https://docs.brightdata.com/proxy-networks/config-options)
