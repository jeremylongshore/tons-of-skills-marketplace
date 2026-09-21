---
name: brightdata-performance-tuning
description: 'Analyze and tune a Bright Data workload from measured phase latency, failure classes, and bounded experiments instead of undocumented provider assumptions. Use when improving throughput or tail latency. Trigger with: "speed up Bright Data", "tune Browser API performance", "reduce snapshot latency".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: "[trace-or-workload]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- web-data
- bright-data
- performance-tuning
- operations
compatibility: 'Requires an approved workload, phase-level telemetry, representative fixtures, and a bounded canary environment'
---
# Bright Data Evidence-Based Performance Tuning

## Overview

Improve the slowest measured phase while preserving authorization, correctness, and cost ceilings. Choose the Bright Data product that matches the interaction, separate provider time from local queue and processing time, change one variable, and retain rollback evidence.

## Prerequisites

- Approved targets and representative request or snapshot fixtures
- Baseline traces for queue, connect, provider, transfer, parse, and downstream phases
- Explicit latency, success, concurrency, byte, and cost thresholds

## Instructions

### Step 1: Build the baseline

Read traces and Grep for serialized work, unbounded concurrency, full-body buffering, repeated browser startup, hot polling, and retry amplification. Segment by product, target class, response size, and error class.

### Step 2: Verify product fit

Use proxy requests for simple HTTP collection, Browser API when a browser session is actually required, and asynchronous scraper snapshots for batch workloads. Do not hide a product mismatch with more concurrency.

### Step 3: Run one-variable experiments

Write or Edit a canary plan that changes only batch size, worker concurrency, connection reuse, browser-session reuse, polling cadence, streaming boundary, or downstream parallelism. Keep admission, byte, and cost ceilings fixed.

### Step 4: Decide from evidence

Compare median and tail latency, success, 429, provider errors, bytes, queue time, and unit cost. Retain changes only when the target metric improves without violating safety, correctness, or budget constraints.

## Tool Discipline

Use Read and Grep for trace and implementation analysis. Use Write and Edit for benchmarks, fixtures, canary configuration, and the decision record. This skill does not generate production load or alter live Bright Data resources.

## Output

- Phase-level baseline and identified bottleneck
- One-variable experiment matrix with ceilings
- Keep or rollback decision supported by metrics

## Examples

A snapshot workload spends most time parsing after download. Streamed NDJSON parsing lowers memory and tail latency in a fixed-size canary while provider concurrency and collection scope remain unchanged.

## Error Handling

| Failure | Meaning | Response |
|---------|---------|----------|
| Baseline mixes unlike products | Comparison is invalid | Segment proxy, Browser API, and snapshot paths |
| Throughput rises with more 429 responses | Concurrency exceeds an effective boundary | Back off and lower admission |
| Faster output loses records | Optimization broke correctness | Roll back and add integrity assertions |

## Resources

- [Browser API introduction](https://docs.brightdata.com/products/scraping-browser/introduction)
- [Download snapshot](https://docs.brightdata.com/api-reference/scrapers/delivery-apis/download-snapshot)
- [Asynchronous scraper workflow](https://docs.brightdata.com/products/scrapers/scrapers-library/async-requests)
- [Proxy error catalog](https://docs.brightdata.com/proxy-networks/errorCatalog)
