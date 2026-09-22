---
name: canva-performance-tuning
description: 'Optimize Canva Connect latency and throughput from measured application evidence. Use when tuning metadata caches, pagination, connection reuse, async-job polling, or endpoint concurrency under explicit freshness and safety budgets. Trigger with: "speed up Canva", "tune Canva polling", "optimize Canva performance".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[endpoint-and-baseline-window]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - performance
  - operations
compatibility: 'Requires a protected benchmark workload, current endpoint contract, and approved latency, freshness, data, and rollback budgets.'
---

# Canva Measured Performance Tuning

## Overview

Change one controlled variable at a time and compare logical-operation outcomes, not just raw request latency. Never cache credentials or assume fixed Canva URL lifetimes and performance guarantees.

## Prerequisites

- Baseline window, normalized endpoint, workload, and local SLO
- Current OpenAPI/response contract and endpoint rate metadata
- Cache data class, freshness/invalidation policy, feature flag, and rollback

## Instructions

### Step 1: Establish a baseline

Use Read and Grep to measure logical operations, provider calls, latency distribution, job completion, retries, cache hits, errors, and queue depth with synthetic or approved data.

### Step 2: Identify the bottleneck

Separate network/connection latency, unnecessary fields, pagination, duplicate reads, write retries, polling cadence, token locks, worker capacity, and local storage.

### Step 3: Design one experiment

Use Write or Edit to change one cache, pagination, connection, queue, or poll control behind a feature flag with explicit success and rollback thresholds.

### Step 4: Protect caches

Cache only approved metadata, key by authorization boundary, encrypt where policy requires, and invalidate on writes, consent/ownership changes, or freshness expiry.

### Step 5: Tune asynchronous polling

Persist job ID, begin with a short local interval, apply bounded exponential backoff, and stop at the application budget while reconciliation continues asynchronously.

### Step 6: Validate and roll out

Compare correctness, freshness, duplicate prevention, resource use, and latency. Roll back on stale authorization, missed completion, increased errors, or throttling.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

A service reduces design-list calls with a tenant- and user-authorized metadata cache. The experiment proves freshness and invalidation before rollout and never stores thumbnail or export URLs durably.

## Error Handling

| Failure | Response |
| --- | --- |
| No baseline exists | Instrument before optimizing |
| Cache serves stale authorization | Disable it and fix ownership/consent invalidation |
| Polling increases 429s | Lower scoped concurrency and widen bounded intervals |
| Latency improves but correctness regresses | Roll back the experiment |

## Resources

- [First-party source notes](references/official-docs.md)
- [API request model](https://www.canva.dev/docs/connect/api-requests-responses/)
- [Latest OpenAPI](https://www.canva.dev/sources/connect/api/latest/api.yml)
