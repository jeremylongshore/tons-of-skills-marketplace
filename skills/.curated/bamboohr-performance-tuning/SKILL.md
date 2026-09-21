---
name: bamboohr-performance-tuning
description: >-
  Improve BambooHR sync throughput with dataset v2 projection, pagination,
  deterministic ordering, bounded concurrency, and measured caching. Use when
  an HR pipeline is slow or creates N+1 traffic. Trigger with "BambooHR
  performance", "BambooHR slow sync", or "optimize BambooHR pipeline".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<pipeline-path> <latency-or-volume-goal>"
version: 1.5.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, hr, bamboohr, performance, datasets]
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# BambooHR Performance Tuning

## Overview

Optimize from a measured request graph while preserving completeness and
privacy. The first objective is usually eliminating per-employee fan-out, not
raising concurrency against an unknown tenant limit.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The tenant, identity, and data scope only when approved live work is in scope.
- The current evidence register plus customer-specific permissions and agreements.

## Current Contract

Dataset v2 returns selected fields with `links` and `meta` pagination and permits
page sizes up to 1000 in the reviewed OpenAPI. Its request uses `filter`,
`orderBy`, `page`, and `pageSize`. Dataset v1 data retrieval and custom-report
paths carry deprecation notices and should not anchor new optimizations.

## Authentication

Benchmark with the same auth mode and effective field permissions as production,
but only in an approved test tenant or sanitized workload. Different identities
can produce different shapes, so never compare results without recording the
credential alias and permission set.

## Instructions

1. Establish baseline p50/p95 latency, request count by operation, page count,
   records and bytes received, retries, error rate, CPU/memory, destination time,
   and end-to-end freshness.
2. Draw the request graph. Replace N+1 employee reads with dataset v2 projections
   where the required fields and semantics are supported.
3. Minimize `fields`, add deterministic `orderBy`, and tune `pageSize` below the
   documented maximum based on payload, memory, latency, and `413` behavior.
4. Stream or page through data and commit checkpoints only after destination
   durability. Do not load the complete workforce into memory by default.
5. Cache stable metadata such as dataset/field definitions with a bounded TTL.
   Do not cache tokens or unrestricted employee payloads in a shared cache.
6. Add per-tenant concurrency control and reuse safe HTTP connections. Increase
   parallelism only during a measured canary and watch `429` and tail latency.
7. Compare exact record identities and reconciliation counts before and after.
   Roll back if freshness, completeness, permissions, or memory regresses.

## Tool Discipline

Use Read, Glob, and Grep to inspect the request graph and current metrics. Use
Write/Edit for approved instrumentation, query changes, and tests. This skill
does not authorize a production benchmark or HR-data export.

## Approval Boundaries

Require approval before querying production, changing field selection or cache
retention, increasing concurrency, or replacing a source endpoint. Performance
does not justify silently omitting inactive or future-dated records.

## Output

Return baseline and candidate metrics, request-graph delta, selected fields and
pagination, cache/concurrency policy, reconciliation proof, canary scope,
rollback thresholds, and measured result.

## Error Handling

- Faster but incomplete: reject the change and restore the last checkpoint.
- `413`: lower page size/field count and remeasure.
- Rising `429` or tail latency: reduce concurrency and open the circuit.
- Schema drift: quarantine the page rather than skipping fields or records.

## Examples

- "Make the nightly sync faster" begins with a request-count and reconciliation baseline.
- "Run 100 workers" is replaced by a per-tenant canary with explicit stop thresholds.

## Resources

Read [official evidence](references/official-docs.md) before altering data access.
