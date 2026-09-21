---
name: brightdata-cost-tuning
description: 'Govern Bright Data usage with product-aware units, workload attribution, budgets, and abort thresholds without hard-coded prices. Use when forecasting or reducing collection spend. Trigger with: "estimate Bright Data cost", "add a Bright Data budget", "reduce Bright Data usage".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: "[workload-or-usage-export]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- web-data
- bright-data
- cost-tuning
- operations
compatibility: 'Requires current account usage data, approved workload ownership, and finance-defined budget thresholds'
---
# Bright Data Cost and Usage Governance

## Overview

Translate an approved workload into measurable provider and internal units, attribute them to an owner, and stop work before cost or scope escapes. Read current account and contract data at decision time; do not encode volatile prices in source.

## Prerequisites

- A workload manifest with owner, purpose, target, fields, product, and schedule
- Current Bright Data usage or billing export and contract terms
- Finance-approved forecast, alert, and abort thresholds

## Instructions

### Step 1: Map cost-driving units

Read usage evidence and Grep the implementation for product choice, attempts, retries, concurrency, bytes, browser time, snapshot records, downloads, delivery, storage, and downstream processing. Label provider-reported units separately from local estimates.

### Step 2: Attribute every operation

Write or Edit a usage envelope containing workload ID, owner, environment, product, target class, maximum attempts, maximum bytes or records, schedule, retention, and approved destination. Reject unattributed operations.

### Step 3: Forecast scenarios

Calculate baseline, expected, and worst-authorized cases from current contract inputs. Model retries and duplicate processing explicitly, but do not assume a global provider request limit or a universal price.

### Step 4: Enforce and reconcile

Add preflight budgets, in-run alerts, hard abort thresholds, and post-run reconciliation against provider evidence. Investigate variance by product, target, failure class, byte volume, and duplicate work before raising a budget.

## Tool Discipline

Use Read and Grep for usage, billing, and implementation inspection. Use Write and Edit for the usage envelope, forecast, alerts, tests, and reconciliation record. This skill does not change a plan, purchase capacity, or run collection traffic.

## Output

- Product-aware unit and ownership map
- Three-scenario forecast with sourced inputs
- Alert, abort, reconciliation, and variance controls

## Examples

A batch has a maximum snapshot-record count, transfer-byte ceiling, retry budget, storage retention, and owner tag. The run stops at its authorized boundary and reconciles provider usage before the next schedule is approved.

## Error Handling

| Failure | Meaning | Response |
|---------|---------|----------|
| Current contract inputs are unavailable | Forecast lacks an authority | Mark cost unknown and block expansion |
| Usage has no workload owner | Spend is unattributed | Quarantine the schedule until ownership is assigned |
| Variance comes from duplicate delivery | Processing is not idempotent | Fix deduplication before increasing the budget |

## Resources

- [REST API authentication](https://docs.brightdata.com/api-reference/authentication)
- [Asynchronous scraper workflow](https://docs.brightdata.com/products/scrapers/scrapers-library/async-requests)
- [Download snapshot](https://docs.brightdata.com/api-reference/scrapers/delivery-apis/download-snapshot)
- [Users management](https://docs.brightdata.com/general/account/users-management)
