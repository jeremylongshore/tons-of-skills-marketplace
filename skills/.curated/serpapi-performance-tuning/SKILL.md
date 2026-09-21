---
name: serpapi-performance-tuning
description: 'Measure and improve SerpAPI latency, payload size, connection reuse, caching, and concurrency without breaking freshness or allowance controls. Use when search performance misses an SLO. Trigger with "tune SerpAPI performance".'
argument-hint: "[engine] [latency-slo] [freshness-slo]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, serpapi, performance, caching, observability]
model: inherit
effort: high
compatibility: Designed for Claude Code; production cache, output, or concurrency changes require owner approval and measured rollback criteria
---
# SerpAPI Evidence-Driven Performance Tuning

## Overview

Optimize the measured bottleneck while preserving result freshness, schema correctness, privacy, and account capacity.

## Prerequisites

- Engine-level latency histograms, payload sizes, error rates, cache hits, and search consumption
- User-facing latency and freshness objectives plus an account throughput budget
- Representative sanitized fixtures and a reversible canary environment

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect call paths and instrumentation, `WebFetch` to verify current cache and output features, and `Write` or `Edit` for measurements, cache layers, field selection, tests, and rollback controls.

## Current Contract

For an exactly matching parameter set, SerpAPI may serve its one-hour server cache; cached searches are free and do not count toward monthly searches. `no_cache=true` forces a fresh fetch and must not be combined with `async`. JSON Restrictor reduces selected JSON fields, and `output=md` provides token-efficient Markdown for agent use.

## Authentication

Keep `SERPAPI_KEY` outside measurement labels, cache keys, traces, and profiles. Treat query values and result bodies according to their data classification.

## Instructions

1. Break total latency into queue, connection, vendor processing, transfer, parsing, and downstream rendering; record p50, p95, and p99.
2. Confirm whether the workload needs structured JSON, restricted JSON, Markdown, or approved raw HTML.
3. Normalize parameters and add an application cache whose key excludes credentials but includes every input that changes semantics.
4. Align cache TTL with the freshness objective; allow the SerpAPI server cache unless a justified fresh-fetch requirement exists.
5. Reuse the official Python client's pooled connections or the supported JavaScript client rather than creating ad hoc transports.
6. Bound concurrency below the live Account API throughput and compare sequential, limited-parallel, and cached paths with fixtures or an approved canary.
7. Promote only if latency improves without worse correctness, privacy, errors, 429s, or search consumption; retain rollback thresholds.

## Output

Return the baseline profile, bottleneck, proposed and measured changes, cache-key/TTL contract, output format, capacity impact, canary results, and rollback thresholds.

## Error Handling

| Condition | Response |
|---|---|
| Cache serves semantically wrong data | Disable the layer and expand the normalized key contract. |
| `no_cache` raises usage unexpectedly | Remove it unless the freshness requirement explicitly justifies fresh fetches. |
| Parallelism causes 429s | Reduce admissions and coordinate through the shared limiter. |
| Field restriction breaks parsing | Restore required fields and lock the projection with fixtures. |

## Example

```text
engine=google; baseline_p95=measured; bottleneck=payload; change=json-restrictor; freshness=1h; search_delta=0; schema-tests=pass; rollback=feature-flag
```

## Resources

- [Google Search SerpAPI parameters](https://serpapi.com/search-api#serpapi-parameters)
- [JSON Restrictor](https://serpapi.com/json-restrictor)
- [Markdown output](https://serpapi.com/markdown)
- [Account API](https://serpapi.com/account-api)

## Next Steps

Observe a full traffic cycle and revisit the tuning decision when freshness, engine mix, or account capacity changes.
