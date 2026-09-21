---
name: flyio-performance-tuning
description: >-
  Analyze and tune Fly.io placement, VM resources, concurrency, autostart behavior, networking, and data locality from measured service objectives. Use when latency or saturation is unacceptable. Trigger with: "speed up Fly app", "tune Fly concurrency", "reduce Fly cold starts".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[app-slo-and-observation-window]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flyio
  - performance
  - concurrency
  - placement
compatibility: 'Requires application service objectives, representative traffic, metrics and health evidence, current Machine sizes, regions, and data dependency placement.'
---

# Fly.io Performance and Placement Tuning

## Overview

Treat performance as an end-to-end path through Anycast routing, Fly Proxy, Machine placement, process concurrency, VM resources, autostart, and data locality. Optimize from percentiles and saturation evidence rather than assuming more regions or larger VMs always help.

## Prerequisites

- Latency, throughput, error, availability, and cold-start objectives
- Per-region request, CPU, memory, concurrency, restart, and dependency latency evidence
- Current image, VM sizes, Machine counts, service concurrency, autostop, and database placement

## Instructions

### Step 1: Establish a representative baseline

Measure regional latency percentiles, errors, throughput, concurrency, CPU, memory, restarts, health transitions, cold starts, and dependency timing.

### Step 2: Locate the bottleneck

Separate network distance, queueing, application work, CPU throttling, memory pressure, startup, connection setup, database latency, and capacity placement.

### Step 3: Tune concurrency with capacity

Align service soft and hard limits with measured per-Machine capacity. Preserve headroom so Fly Proxy can route around unhealthy or saturated Machines.

### Step 4: Tune lifecycle behavior

Compare always-running, stopped, and suspended behavior. Autostart can reduce idle cost but adds startup delay; set minimum running capacity from the service objective.

### Step 5: Align placement with state

Add or remove regions based on user and dependency latency, available capacity, residency, and data topology. Keep region-bound volumes and database writes explicit.

### Step 6: Change one variable and verify

Canary a single resource, count, concurrency, lifecycle, or placement adjustment; compare the same observation window and roll back on regression.

## Authentication

Use read-only access for metrics, health, state, and placement analysis. Resource or scaling changes require a deploy-capable scoped identity and explicit approval. Performance evidence must not include tokens, request bodies, or sensitive labels.

## Tool Discipline

Use Read and Grep to inspect application configuration, deployment evidence, provider documentation, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for an approved plan, configuration, implementation, test, or redacted receipt. Do not create, deploy, scale, restart, stop, suspend, destroy, rotate, revoke, expose, or migrate live Fly.io resources without explicit operator approval.

## Output

- Regional performance baseline and bottleneck hypothesis
- Ranked experiment plan with one variable, expected effect, risk, and rollback per test
- Before/after service-objective and resource reconciliation

Return the target organization, app, environment, region set, Machine or database identifiers, source-contract fingerprint, evidence, unresolved risks, rollback state, and final decision without exposing tokens, secrets, connection strings, or customer data.

## Examples

A globally routed API shows good edge latency but poor database calls outside the primary region. The operator avoids adding more web regions, first tests connection reuse and regional request routing, then measures the same percentile window before deciding on topology changes.

## Error Handling

| Failure | Response |
| --- | --- |
| Metrics disagree with user impact | Validate time window, region, labels, sampling, and synthetic versus real traffic before tuning. |
| Autostart causes latency spikes | Increase minimum running capacity or revert lifecycle settings while preserving the cost finding. |
| One region is capacity constrained | Choose from current placement options, retain fallback capacity, and do not promise permanent regional availability. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [Metrics](https://fly.io/docs/monitoring/metrics/)
- [Autostop and autostart](https://fly.io/docs/reference/fly-proxy-autostop-autostart/)
- [Regions](https://fly.io/docs/reference/regions/)
- [Private networking](https://fly.io/docs/networking/private-networking/)
