---
name: clari-rate-limits
description: >-
  Analyze and schedule Clari exports, ingestion jobs, and Copilot reads within provider concurrency and quota controls. Use when preventing 429 responses or coordinating workers. Trigger with: "handle Clari rate limits", "schedule Clari jobs", "recover from Clari 429".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[surface-workload-and-service-level-objective]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - clari
  - rate-limits
  - quota
  - scheduling
compatibility: 'Requires workload volume estimates, retained job or pagination state, and access to organization limits where the provider exposes them.'
---

# Clari Quota-Aware Request Scheduling

## Overview

Model each Clari surface as its own constrained queue. Revenue exports consume organization-level concurrent and rolling quota capacity, ingestion can reject excess concurrent async jobs, and Copilot has documented per-second and weekly ceilings.

## Prerequisites

- Request inventory split by Revenue export, ingestion, and Copilot
- Priority classes, latency objectives, and retry budget
- Durable job IDs, cursors, and deduplication keys

## Instructions

### Step 1: Read the applicable limits

Use `/admin/limits` for Revenue export capacity and record the Copilot 10-per-second and 100,000-per-week ceilings from the current contract.

### Step 2: Allocate capacity

Reserve headroom for interactive or recovery work and assign explicit concurrency to each scheduler rather than letting every worker retry independently.

### Step 3: Make work resumable

Persist export job IDs, ingestion job IDs, Copilot cursors, and request fingerprints before polling or retrying.

### Step 4: Apply bounded backoff

Honor provider retry guidance when present; otherwise use capped exponential backoff with jitter and a maximum elapsed time.

### Step 5: Prevent duplicate mutations

Before replaying a queue or ingestion request, reconcile retained state and provider jobs. Reads may resume from checkpoints; writes require an explicit idempotency decision.

### Step 6: Measure and tune

Track queue delay, attempts, 429 rate, quota remaining, terminal latency, and abandoned work by surface.

## Authentication

Limit reads and job polling still require the correct surface credential. Redact authentication headers and keep scheduler state free of secret values and customer payloads.

## Tool Discipline

Use Read and Grep to inspect configuration, provider contracts, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not issue, rotate, revoke, create, update, cancel, delete, export, ingest, or publish provider data without explicit operator approval.

## Output

- Per-surface capacity model and worker allocation
- Retry, checkpoint, and deduplication policy
- Quota dashboard with alert and shedding thresholds

Return the exact surface, environment, resource or job identifiers, contract fingerprint, evidence, unresolved risks, and final decision without exposing credentials or sensitive customer data.

## Examples

A scheduler permits at most the organization’s reported export concurrency minus one recovery slot, polls known job IDs with jitter, and independently throttles Copilot reads below both documented ceilings.

## Error Handling

| Failure | Response |
| --- | --- |
| Limits endpoint is unavailable | Use the last verified lower bound, reduce concurrency, and alert rather than guessing upward. |
| 429 recurs after backoff | Open the circuit, preserve checkpoints, and reduce admission until the provider window clears. |
| Quota is exhausted | Defer noncritical exports and obtain an approved quota or cadence change before resuming. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Clari Revenue API reference](https://developer.clari.com/default/documentation/external_spec)
- [Clari Copilot API reference](https://api-doc.copilot.clari.com/)
