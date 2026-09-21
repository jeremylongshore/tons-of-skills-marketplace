---
name: clari-cost-tuning
description: >-
  Analyze and optimize Clari integration consumption across export quota, Copilot requests, transfer, storage, and warehouse work. Use when reducing unnecessary runs. Trigger with: "reduce Clari cost", "budget Clari exports", "tune Clari retention".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[workload-retention-and-budget-objective]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - clari
  - cost-governance
  - quota
  - retention
compatibility: 'Requires workload inventory, organization limit evidence, destination usage metrics, and an approved freshness and retention policy.'
---

# Clari Export and Data-Cost Governance

## Overview

Optimize total integration consumption without inventing public Clari price claims. Provider request capacity, large result transfer, raw-data retention, repeated transformations, and warehouse scans are measurable levers even when commercial pricing is contract-specific.

## Prerequisites

- Export and Copilot request counts by workload and owner
- Result bytes, rows, retention, storage, and warehouse scan metrics
- Freshness, recovery, audit, and analytical requirements

## Instructions

### Step 1: Attribute consumption

Tag every scheduled or ad hoc request with owner, business outcome, surface, window, selected data, and destination.

### Step 2: Measure the full path

Track export quota, Copilot calls, result size, transfer, landing retention, transformation compute, warehouse storage, and query scans.

### Step 3: Remove redundant work

Reuse immutable approved snapshots, coalesce identical requests, narrow history and fields, and resume from checkpoints instead of full reruns.

### Step 4: Set freshness tiers

Give operational, analytical, audit, and backfill workloads explicit cadences and defer low-value work when quota or budget is constrained.

### Step 5: Tune retention and layout

Keep raw data only as policy requires, compact normalized data, partition by access pattern, and preserve lineage even when payloads expire.

### Step 6: Review tradeoffs

Compare consumption savings with freshness, recovery, correctness, and compliance impact before promoting a change.

## Authentication

Consumption telemetry must contain credential references and workload identifiers, never secret values or sensitive payloads. Do not create additional tokens to bypass organization limits.

## Tool Discipline

Use Read and Grep to inspect configuration, provider contracts, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not issue, rotate, revoke, create, update, cancel, delete, export, ingest, or publish provider data without explicit operator approval.

## Output

- Workload-level consumption and ownership ledger
- Quota, request, storage, and warehouse budget policy
- Before/after savings with freshness, correctness, and recovery impact

Return the exact surface, environment, resource or job identifiers, contract fingerprint, evidence, unresolved risks, and final decision without exposing credentials or sensitive customer data.

## Examples

A team replaces six overlapping quarterly exports with one immutable snapshot shared by approved consumers, retains raw data only for the required window, and preserves separate transformations and lineage.

## Error Handling

| Failure | Response |
| --- | --- |
| Savings reduce required freshness | Restore the approved cadence for the affected service level. |
| Shared snapshot mixes authorization scopes | Separate exports and storage boundaries even if consumption increases. |
| Quota attribution is missing | Pause noncritical schedules until owners and business purposes are recorded. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Clari Revenue API reference](https://developer.clari.com/default/documentation/external_spec)
- [Clari Copilot API reference](https://api-doc.copilot.clari.com/)
