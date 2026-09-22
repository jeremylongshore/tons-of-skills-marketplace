---
name: clari-performance-tuning
description: >-
  Optimize Clari integration latency without violating concurrency, quota, correctness, or duplicate-work controls. Use when exports or Copilot extraction miss an SLO. Trigger with: "speed up Clari exports", "tune Clari polling", "reduce Clari pipeline latency".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[surface-workload-baseline-and-slo]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - clari
  - performance
  - throughput
  - latency
compatibility: 'Requires timing telemetry by stage, provider capacity evidence, representative workloads, and a rollbackable tuning boundary.'
---

# Clari Pipeline Throughput Tuning

## Overview

Tune from measured stage latency instead of increasing concurrency blindly. Provider queue time, polling, result transfer, parsing, reconciliation, and destination load are separate bottlenecks with different safe remedies.

## Prerequisites

- Baseline p50, p95, and failure rate for each pipeline stage
- Request sizes, selected fields, periods, pages, and destination load profile
- Current organization limits and Copilot ceilings

## Instructions

### Step 1: Build the latency budget

Split the service-level objective across queue admission, provider execution, polling, transfer, validation, and publication.

### Step 2: Locate the bottleneck

Correlate provider job timing, response size, page count, local CPU and memory, warehouse load, and retry delay.

### Step 3: Reduce unnecessary work

Narrow forecast data types, history, scope, Copilot details, and rerun windows while preserving the approved analytical contract.

### Step 4: Tune polling and paging

Use state-aware backoff, durable cursors, bounded page sizes, and streaming validation; do not poll faster than useful state changes.

### Step 5: Use concurrency within evidence

Increase independent reads or transforms only inside reported provider and destination headroom, retaining a recovery slot.

### Step 6: Canary and compare

Run the candidate against the same representative workload, compare correctness and cost signals, and roll back if either regresses.

## Authentication

Performance telemetry must omit credentials and sensitive payloads. Never duplicate tokens across workers to evade organization or workspace limits.

## Tool Discipline

Use Read and Grep to inspect configuration, provider contracts, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not issue, rotate, revoke, create, update, cancel, delete, export, ingest, or publish provider data without explicit operator approval.

## Output

- Stage-level latency profile and identified bottleneck
- Tuning change with provider-capacity rationale
- Before/after correctness, latency, quota, and rollback results

Return the exact surface, environment, resource or job identifiers, contract fingerprint, evidence, unresolved risks, and final decision without exposing credentials or sensitive customer data.

## Examples

Profiling shows warehouse parsing—not provider export time—dominates latency. The team streams validation and batches warehouse writes while leaving Clari concurrency unchanged.

## Error Handling

| Failure | Response |
| --- | --- |
| Latency improves but rows diverge | Reject the tuning and restore the verified transform or publication path. |
| Concurrency causes 429 responses | Reduce admission, preserve checkpoints, and remeasure within documented capacity. |
| Result size exhausts memory | Stream or chunk local processing without altering provider semantics or dropping validation. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Clari Revenue API reference](https://developer.clari.com/default/documentation/external_spec)
- [Clari Copilot API reference](https://api-doc.copilot.clari.com/)
