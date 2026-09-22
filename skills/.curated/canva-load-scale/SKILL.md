---
name: canva-load-scale
description: 'Design a mock-first Canva capacity test and a tightly authorized provider probe. Use when sizing queues, workers, token-refresh serialization, or endpoint concurrency without inventing universal quotas. Trigger with: "load test Canva", "size Canva workers", "Canva capacity plan".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[approved-load-profile-and-environment]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - scale
  - operations
compatibility: 'Provider load testing requires explicit authorization, dedicated non-production users, synthetic data, and an abort owner.'
---

# Canva Bounded Capacity Test

## Overview

Measure your application under a declared workload while honoring endpoint-specific Canva metadata and actual responses. Default to mocks; a live probe must be small, reversible, and isolated.

## Prerequisites

- Approved workload model, test target, user count, and abort thresholds
- Mock contract plus current endpoint rate metadata
- Synthetic assets, dedicated users, cleanup plan, and provider-test authorization

## Instructions

### Step 1: Model operations

Define logical reads, writes, async submissions, polling, refresh, and webhook processing separately. Include bursts, retries, and job completion distribution.

### Step 2: Exercise mocks first

Use Write or Edit to implement contract-faithful responses for success, throttling, auth failure, in-progress, terminal failure, and schema drift.

### Step 3: Size application limits

Measure queue depth, worker utilization, latency, memory, refresh lock contention, and database pressure; set local admission and concurrency below measured safe points.

### Step 4: Authorize a provider probe

Limit it to named endpoint/user, request count, duration, and synthetic data. Avoid mutating operations unless their cleanup and duplicate impact are approved.

### Step 5: Abort aggressively

Stop on unexpected authorization, data, sustained throttling, provider error, cleanup failure, or impact outside the named test.

### Step 6: Produce capacity evidence

Use Write or Edit to record workload, environment, contract version, aggregate results, observed provider responses, chosen headroom, and rollback.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

A mock workload proves the export ledger and polling workers at expected burst. A small authorized live read then validates only endpoint behavior; it does not attempt to discover Canva's limits by saturation.

## Error Handling

| Failure | Response |
| --- | --- |
| No provider-test authorization | Run mocks only |
| Throttle response appears | Stop the live probe and lower the scoped rate |
| Refresh lock contention grows | Serialize per user and resize from measured evidence |
| Cleanup cannot be verified | Do not run mutating load cases |

## Resources

- [First-party source notes](references/official-docs.md)
- [API request model](https://www.canva.dev/docs/connect/api-requests-responses/)
- [Latest OpenAPI](https://www.canva.dev/sources/connect/api/latest/api.yml)
