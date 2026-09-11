---
name: salesforce-load-scale
description: 'Test Salesforce integration capacity in an authorized non-production org with synthetic data, bounded load, org limits, and business-invariant checks. Use when planning scale. Trigger with "load test Salesforce".'
argument-hint: "[workload] [non-production-org]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, load-testing, capacity, synthetic-data]
model: inherit
effort: high
compatibility: Designed for Claude Code; load generation, org capacity consumption, and automation effects require platform and environment-owner approval
---
# Salesforce Bounded Load and Scale Validation

## Overview

Measure useful throughput and failure behavior without treating Salesforce as an unconstrained HTTP endpoint or using production records as test data.

## Prerequisites

- Representative workload mix, service objectives, business invariants, expected growth, and capacity owner
- Dedicated authorized org, synthetic dataset, matching automation where possible, current limits, and peer-workload schedule
- Load stages, concurrency ceilings, stop thresholds, cleanup, reconciliation, and incident contacts

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce enforces org-, edition-, license-, API-, Apex-, bulk-, event-, and concurrency-dependent limits. Limits and usage must be discovered in the target org, and non-production fidelity to production must be documented.

## Authentication

Use a dedicated non-production principal with minimum objects and fields. Keep authorization outside load scripts and prevent tools, results, and fixtures from containing production tokens or personal data.

## Instructions

1. Model read, write, query, bulk, composite, async, and event workload proportions plus business deadlines and growth.
2. Capture org identity, edition, features, metadata, automation, relevant limits, peer workloads, and fidelity gaps.
3. Generate synthetic records with stable keys and safe relationships; precompute expected counts and outcomes.
4. Define stepped load, warm-up, duration, concurrency, request budget, stop thresholds, cooldown, cleanup, and rollback.
5. Run small stages while measuring latency, throughput, errors, limits, locks, async lag, event lag, automation, and business outcomes.
6. Stop on the first approved threshold; never retry hard limits or uncertain writes as additional load.
7. Reconcile all generated data and events, delete fixtures, restore settings, compare capacity to objectives, and state extrapolation limits.

## Approval Boundaries

Do not point load tools at production, use real customer data, exceed the approved budget, disable automation, or raise concurrency after a breach.

## Output

Return the workload model, org and fidelity evidence, synthetic dataset, stage results, thresholds, bottleneck, invariant checks, cleanup, and capacity recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Test org differs materially from production | Report the fidelity gap and do not claim production capacity from the result. |
| Limits or locks breach the stop threshold | Terminate the stage, preserve evidence, and reconcile before another test. |
| Synthetic cleanup is incomplete | Keep the environment quarantined and assign cleanup before reuse. |

## Example

A redacted completion receipt might look like this:

```text
workload=case-sync; org=performance-sandbox; data=synthetic; stages=5; stop=stage4-locks; cleanup=complete; extrapolation=bounded
```

## Resources

- [REST API limits](https://developer.salesforce.com/docs/platform/api-rest/guide/resources-limits.html)
- [Bulk API 2.0](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/bulk_api_2_0.htm)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
