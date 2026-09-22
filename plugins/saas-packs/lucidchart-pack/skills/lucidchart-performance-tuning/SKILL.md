---
name: lucidchart-performance-tuning
description: 'Measure and improve Lucid Standard Import, export, editor extension, or data connector performance without weakening correctness. Use when Lucid workflows are slow or resource-heavy. Trigger with "optimize Lucid performance".'
argument-hint: "[project-path] [scenario]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, lucidchart, performance, standard-import, extensions]
model: inherit
effort: high
compatibility: Designed for Claude Code; production profiling or live load tests require service, data, and account-owner approval
---
# Evidence-Driven Lucid Performance Tuning

## Overview

Tune one measured workflow at a time while preserving document fidelity, data reconciliation, authorization, and documented limits.

## Prerequisites

- A reproducible scenario, representative sanitized fixture, baseline, and service objective
- Component classification: import, export, REST operation, editor extension, or connector
- Owners for data correctness and any live environment

## Tool Discipline

Use `Read`, `Glob`, and `Grep` for code, fixtures, and receipts, `WebFetch` for current limits/contracts, and `Write` or `Edit` only for local benchmarks, scoped improvements, and reports.

## Current Contract

Each Lucid surface has different constraints. Standard Import performance depends on archive structure, uncompressed assets, pages, objects, and data; extension/connector performance depends on the installed SDK, transforms, network behavior, and UI work. Rate limits are endpoint-specific.

## Authentication

Benchmark offline first. Use dedicated test credentials and synthetic data for live measurements. Never log tokens or expose restricted document data in traces.

## Instructions

1. Define the user-visible objective and correctness invariants before measuring.
2. Record versions, fixture digest, cold/warm state, network assumptions, concurrency, and timing method.
3. Establish at least three comparable baseline samples with latency distribution and resource counts.
4. Profile the dominant phase: archive generation/upload/render, export polling/download, extension transform/UI, or connector fetch/reconcile.
5. Propose one reversible change such as bounded batching, deduplication, incremental reconciliation, asset reduction, caching with invalidation, or deferred UI work.
6. Run the same samples and compare latency, memory, requests, payload, rejects, document fidelity, and reconciliation.
7. Present any live load increase or concurrency change for approval; honor endpoint-specific limits and backpressure.
8. Keep only improvements that meet both performance and correctness thresholds.

## Approval Boundaries

Do not load-test Lucid or a source system, increase concurrency, reduce validation, or alter production documents without approval.

## Output

Return scenario, versions, baseline and candidate distributions, bottleneck evidence, correctness checks, limits consulted, decision, and rollback.

## Error Handling

| Condition | Response |
|---|---|
| Results are noisy | Control the environment and increase samples; do not declare a win. |
| Faster result changes document/data | Reject the optimization and preserve the failing fixture. |
| 429 or service degradation appears | Stop load, honor server guidance, and reduce pressure. |

## Example

```text
scenario=fixture-import; n=5; p50-before=4.8s; p50-after=3.6s; fidelity=pass; requests-delta=0
```

## Resources

- [Official documentation map](references/official-docs.md)

## Next Steps

Add the representative benchmark and correctness assertions to the release regression suite.
