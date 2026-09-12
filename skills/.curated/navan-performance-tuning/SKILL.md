---
name: navan-performance-tuning
description: >-
  Tune a Navan data pipeline against measured vendor, destination, privacy, and deadline constraints. Use when extraction or reconciliation misses its service objective. Trigger with "speed up Navan sync", "Navan latency", or "Navan pipeline performance".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<surface> <workload> <service-objective>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, performance]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Pipeline Performance Tuning

## Overview

Tune a Navan data pipeline against measured vendor, destination, privacy, and deadline constraints. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Optimize after measuring time in authentication, source wait, transfer, parsing, mapping, destination, and reconciliation. Preserve correctness and sensitive-data controls before increasing pages, batches, concurrency, or cache duration.

## Authentication

Benchmark with non-production or approved synthetic data and least-privilege credentials. Do not expose tenant data in profilers, traces, or third-party performance tools.

## Instructions

1. Define latency, freshness, throughput, and reconciliation objectives.
2. Measure each stage with content-free timings and counts.
3. Identify the narrowest documented source or destination constraint.
4. Reduce fields, windows, transformations, or round trips before adding concurrency.
5. Tune bounded queues, checkpoints, backpressure, and destination batches.
6. Canary changes and compare correctness, privacy, and cost alongside speed.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Load tests, production traces, cache or retention changes, higher concurrency, new infrastructure, and deadline tradeoffs require approval.

## Error Handling

- Do not optimize by dropping reconciliation or redaction.
- A faster partial sync is a failure.
- Roll back when errors, queue age, or unexplained totals worsen.

## Output

Return baseline and candidate measurements, bottleneck evidence, chosen controls, correctness deltas, and rollback threshold. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Reduce an oversized extraction window before raising concurrency.
- Batch destination writes while keeping source checkpoints durable.

## Validation

Run cold, steady, burst, throttled, destination-slow, restart, and rollback scenarios with identical fixtures. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
