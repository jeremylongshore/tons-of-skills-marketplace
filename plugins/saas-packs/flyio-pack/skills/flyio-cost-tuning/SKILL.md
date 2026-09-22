---
name: flyio-cost-tuning
description: >-
  Analyze Fly.io Machine, volume, network, IP, and Managed Postgres cost drivers without freezing volatile prices. Use when reducing spend or forecasting capacity. Trigger with: "audit Fly bill", "right-size Fly Machines", "reduce Fly idle cost".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[organization-app-and-billing-window]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flyio
  - cost-management
  - right-sizing
  - autostop
compatibility: 'Requires current billing exports or invoices, app and database inventory, utilization evidence, service objectives, and an approved optimization window.'
---

# Fly.io Cost and Capacity Review

## Overview

Optimize from measured usage and the current pricing page, not copied monthly constants. Separate running and stopped Machine charges, persistent volume and snapshot charges, network and IP costs, and Managed Postgres resources that live outside application deletion.

## Prerequisites

- Billing window, currency, organization, apps, and cost owner
- Machine state and resource history plus traffic, latency, and availability objectives
- Inventory of volumes, snapshots, IPs, transfer, builders, and Managed Postgres clusters

## Instructions

### Step 1: Reconcile the bill to resources

Map each charge class to current Machines, volumes, snapshots, addresses, transfer, builders, and databases. Include unattached and stopped-resource dependencies.

### Step 2: Measure utilization and state

Compare CPU, memory, concurrency, request, latency, restart, and running-time signals with the selected VM size and Machine count.

### Step 3: Evaluate autostop safely

For eligible service apps, model `auto_stop_machines` as `stop` or `suspend` with `auto_start_machines` and a deliberate minimum-running setting. Include cold-start and state-safety costs.

### Step 4: Right-size and place

Change one dimension at a time: VM preset, additional memory, count, region placement, or database plan. Preserve capacity and recovery headroom.

### Step 5: Remove orphaned cost with approval

Identify unattached volumes, obsolete snapshots beyond policy, unused addresses, old builders, and databases no longer referenced. Deletion requires owner confirmation and recovery evidence.

### Step 6: Verify savings and service health

Compare the next billing interval and performance signals with the baseline; reverse changes that violate latency, availability, or recovery objectives.

## Authentication

Prefer read-only organization tokens for inventory and billing analysis. Cost review does not authorize deleting Machines, volumes, addresses, snapshots, or Managed Postgres clusters; obtain resource-owner approval and preserve recovery evidence first.

## Tool Discipline

Use Read and Grep to inspect application configuration, deployment evidence, provider documentation, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for an approved plan, configuration, implementation, test, or redacted receipt. Do not create, deploy, scale, restart, stop, suspend, destroy, rotate, revoke, expose, or migrate live Fly.io resources without explicit operator approval.

## Output

- Cost allocation by resource class and owner
- Ranked optimization plan with forecast, risk, and rollback
- Post-change cost and service-objective comparison

Return the target organization, app, environment, region set, Machine or database identifiers, source-contract fingerprint, evidence, unresolved risks, rollback state, and final decision without exposing tokens, secrets, connection strings, or customer data.

## Examples

An internal HTTP app has predictable idle nights. The operator confirms it has no unsafe local state, models suspend and autostart with one minimum Machine during business hours, preserves volume charges in the forecast, and validates cold-start latency before rollout.

## Error Handling

| Failure | Response |
| --- | --- |
| Bill and inventory do not reconcile | Check deleted apps, stopped Machines, orphaned volumes, addresses, builders, transfer, and Managed Postgres outside app scope. |
| Autostop harms availability | Raise minimum capacity or revert the setting; do not optimize through an unmeasured outage. |
| Pricing changed | Re-fetch the official pricing page and recompute; never preserve a stale copied rate. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [Resource pricing](https://fly.io/docs/about/pricing/)
- [Autostop and autostart](https://fly.io/docs/reference/fly-proxy-autostop-autostart/)
- [Managed Postgres](https://fly.io/docs/mpg/)
