---
name: procore-performance-tuning
description: >-
  Reduce Procore synchronization latency through measured call sequencing, endpoint-specific pagination, caching, batching, and bounded concurrency. Use when a connector is slow, request-heavy, or accumulating lag. Trigger with: "speed up Procore sync", "optimize Procore pagination", "reduce Procore integration latency".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[sync-workload-and-latency-objective]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - performance
  - synchronization
compatibility: 'Requires route-level timing, call-count, pagination, rate-header, and backlog measurements for the target Procore workload.'
---

# Procore Measured Sync Performance

## Overview

Optimize useful records per request and end-to-end freshness before increasing concurrency. Procore recommends collection reads, caching, webhooks, and deliberate sequencing; page limits and response shapes remain endpoint-specific.

## Prerequisites

- Baseline volume, latency percentiles, call count, error rate, and backlog age
- Resource dependency graph and current endpoint pagination contracts
- Correctness oracle for completeness, ordering, duplicates, and deletions

## Instructions

### Step 1: Measure the critical path

Group calls by normalized route and outcome. Identify serial dependency edges, repeated lookups, first-page-only defects, payload-heavy reads, and failed calls consuming budget.

### Step 2: Sequence dependencies

Fetch company and project context before project resources, and prerequisite catalogs before dependent records. Avoid nested request waterfalls when one collection or cache can serve many records.

### Step 3: Paginate correctly

Use each endpoint's documented `per_page` range and follow `Link` relations until `next` is absent. Never treat a global page-size recommendation as an endpoint guarantee.

### Step 4: Reduce redundant work

Cache stable lookups, use webhooks for fast change detection, retain a periodic reconciliation scan, and use documented sync actions where the resource supports them.

### Step 5: Tune concurrency

Increase workers gradually while observing rate headers, error rate, and provider latency. Route every worker through the shared rate controller.

### Step 6: Verify correctness and gain

Compare record sets and state hashes before and after optimization. Accept the change only when completeness is unchanged and measured latency or call volume improves.

## Authentication

Performance tests use the normal OAuth 2.0 Bearer token and company boundary. Never spread traffic across extra credentials to hide inefficient behavior or bypass provider controls.

## Tool Discipline

Use Read and Grep to inspect traces, endpoint contracts, and synchronization code. Use Write or Edit only for the approved optimization, test, measurement, or receipt; avoid uncontrolled production load tests.

## Output

- Before-and-after latency, volume, error, and backlog measurements
- Correctness comparison and endpoint-specific pagination evidence
- Accepted change, rejected experiments, and rollback threshold

Return the bottleneck, hypothesis, measured result, correctness verdict, and operational limit.

## Examples

A connector replaces per-record project lookups with one cached collection, follows every Link next relation, and uses webhook events to prioritize changed records. A reconciliation scan still proves completeness after missed or delayed notifications.

## Error Handling

| Failure | Response |
| --- | --- |
| Throughput improves but records differ | Reject the optimization and restore the prior path. |
| 429 rate increases | Lower concurrency and repair request efficiency before requesting more capacity. |
| Endpoint lacks pagination | Follow that endpoint's contract; do not add generic page parameters. |
| Metrics cannot separate routes | Add route-level telemetry before tuning. |

## Resources

- [First-party source notes](references/official-docs.md)
- [API call sequencing](https://developers.procore.com/documentation/api-call-sequencing)
- [Pagination](https://developers.procore.com/documentation/pagination)
- [API usage guidelines](https://developers.procore.com/documentation/api-usage-guidelines)
