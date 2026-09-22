---
name: flyio-core-workflow-b
description: >-
  Design Fly.io Managed Postgres, Fly Volumes, and private 6PN connectivity with explicit durability boundaries. Use when an app needs persistent data or private service access. Trigger with: "add Fly Managed Postgres", "plan Fly volume storage", "connect Fly apps privately".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[app-database-storage-and-region-plan]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flyio
  - managed-postgres
  - volumes
  - private-networking
compatibility: 'Requires a Fly.io organization, approved data classification and regions, a backup objective, and access to the relevant app and Managed Postgres controls.'
---

# Fly.io Managed Data and Private Networking

## Overview

Choose the data service before writing commands: Managed Postgres is a separate fully managed service, while Fly Volumes are region-bound local NVMe storage attached to Machines. Private 6PN networking connects apps in the same organization but does not make either storage model globally consistent.

## Prerequisites

- Workload, data classification, residency, availability, recovery, and latency requirements
- Approved regions and network boundary
- Restore-test owner and application cutover plan

## Instructions

### Step 1: Select the persistence model

Use Managed Postgres when the workload needs the provider-managed database service. Use a Fly Volume only for software that owns replication and recovery or for region-local state.

### Step 2: Place data intentionally

Choose a supported Managed Postgres region close to the app or create volumes in the same region as their Machines. Query current region availability instead of hardcoding a global count.

### Step 3: Define private connectivity

Use organization 6PN addresses and the documented `.internal` DNS name appropriate to the service, region, process group, or Machine. Document cross-organization exceptions separately.

### Step 4: Protect the data

For Managed Postgres, capture plan, backup, failover, pooling, and support boundaries. For volumes, set snapshot retention and add independent backup or replication when recovery objectives exceed snapshot coverage.

### Step 5: Test failure and restore

Prove application reconnect behavior, credential rotation, snapshot or managed restore procedure, regional loss response, and data reconciliation in a non-production target.

### Step 6: Cut over with rollback

Freeze writes if required, migrate through an approved method, validate counts and application behavior, then retain the old data path until rollback expiry.

## Authentication

Keep database credentials in Fly App secrets or an approved external secret manager, not in `fly.toml` or receipts. Use a scoped Fly.io identity for resource operations and a separate least-privilege database role for application access.

## Tool Discipline

Use Read and Grep to inspect application configuration, deployment evidence, provider documentation, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for an approved plan, configuration, implementation, test, or redacted receipt. Do not create, deploy, scale, restart, stop, suspend, destroy, rotate, revoke, expose, or migrate live Fly.io resources without explicit operator approval.

## Output

- Persistence decision record distinguishing Managed Postgres from Machine volumes
- Region, network, backup, restore, and cutover plan
- Recovery exercise and post-cutover reconciliation receipt

Return the target organization, app, environment, region set, Machine or database identifiers, source-contract fingerprint, evidence, unresolved risks, rollback state, and final decision without exposing tokens, secrets, connection strings, or customer data.

## Examples

A customer API uses Managed Postgres in a supported region and connects over its organization 6PN. A separate cache uses a disposable volume. The operator validates pooling and restore procedures and never describes the cache volume as a replicated database.

## Error Handling

| Failure | Response |
| --- | --- |
| Region is unsupported or capacity constrained | Select from the current provider region listing and re-evaluate latency and residency; do not assume placement. |
| Private DNS returns no address | Check organization, service name, and Machine state; stopped Machines are omitted from AAAA responses. |
| Restore cannot meet the objective | Stop production cutover and revise retention, replication, export, or managed-service plan. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [Managed Postgres](https://fly.io/docs/mpg/)
- [Fly Volumes](https://fly.io/docs/volumes/)
- [Volume snapshots](https://fly.io/docs/volumes/snapshots/)
- [Private networking](https://fly.io/docs/networking/private-networking/)
