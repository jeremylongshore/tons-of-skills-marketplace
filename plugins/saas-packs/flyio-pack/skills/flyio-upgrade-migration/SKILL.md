---
name: flyio-upgrade-migration
description: >-
  Migrate Fly.io app configuration, runtime images, Machine resources, regions, volumes, or Managed Postgres through staged change control. Use when upgrading a live workload. Trigger with: "upgrade Fly app", "migrate Fly region", "change Fly runtime safely".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[app-change-source-and-target]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flyio
  - migration
  - upgrade
  - change-control
compatibility: 'Requires current and target contracts, an immutable backup or export where data is involved, a representative staging boundary, and approved rollback criteria.'
---

# Fly.io Runtime and Platform Change Control

## Overview

Replace the obsolete Apps v1-to-v2 tutorial with ongoing change control for the current Machines platform. Treat flyctl, `fly.toml`, images, architecture, Machine resources, regions, volumes, and Managed Postgres as separate migration surfaces with distinct rollback and data risks.

## Prerequisites

- Current and target versions, configuration, image, architecture, resources, regions, and data topology
- Provider documentation and release notes retrieved at the change boundary
- Backup, export, restore test, acceptance gates, owner, approver, and rollback window

## Instructions

### Step 1: Classify the change surface

Separate CLI behavior, config schema, API contract, image or runtime, CPU architecture, VM size, region placement, volume state, and Managed Postgres changes.

### Step 2: Freeze current state and contract

Record flyctl version, image, Machine instance versions, configuration hash, health, regions, volumes and snapshots, database plan and version, and dependency compatibility.

### Step 3: Build a staging rehearsal

Use production-like configuration with synthetic or protected copied data. Exercise application startup, release command, health, connectivity, schema compatibility, and restore.

### Step 4: Plan data movement explicitly

For a region-bound volume, create and verify the supported copy or snapshot path before Machine movement. For Managed Postgres, follow its current service features and support path; do not apply unmanaged Postgres commands.

### Step 5: Canary the approved change

Change one process group, Machine, or non-production database boundary first. Observe health, errors, latency, data counts, and dependent services for the agreed window.

### Step 6: Complete or reverse

Roll through remaining resources only after acceptance. Reconcile every image, instance version, region, volume attachment, and data count; retain rollback assets until expiry.

## Authentication

Use a scoped deploy identity for app or Machine changes and a separate least-privilege database identity for data verification. Upgrade work does not authorize exposing snapshots, connection strings, or customer data to local or unapproved systems.

## Tool Discipline

Use Read and Grep to inspect application configuration, deployment evidence, provider documentation, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for an approved plan, configuration, implementation, test, or redacted receipt. Do not create, deploy, scale, restart, stop, suspend, destroy, rotate, revoke, expose, or migrate live Fly.io resources without explicit operator approval.

## Output

- Current-to-target contract and compatibility matrix
- Staging, backup, restore, canary, rollout, reconciliation, and rollback plan
- Migration receipt with resource versions, data evidence, exceptions, and rollback-asset expiry

Return the target organization, app, environment, region set, Machine or database identifiers, source-contract fingerprint, evidence, unresolved risks, rollback state, and final decision without exposing tokens, secrets, connection strings, or customer data.

## Examples

An app moves to a new runtime image and VM size. The operator pins current and target images, rehearses startup and release commands, updates one stateless Machine, observes health and latency, then rolls forward. A separate volume move uses a verified snapshot and restore path.

## Error Handling

| Failure | Response |
| --- | --- |
| Provider contract changed during migration | Pause, refresh documentation and client schemas, and reapprove the plan. |
| Canary is incompatible with attached storage | Use rolling or a data-specific migration path; do not force the strategy. |
| Data reconciliation differs | Stop writes or rollout as planned, preserve both sides, and restore or reverse before the rollback window closes. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [flyctl releases](https://github.com/superfly/flyctl/releases)
- [Machine states](https://fly.io/docs/machines/machine-states/)
- [Volume snapshots](https://fly.io/docs/volumes/snapshots/)
- [Managed Postgres](https://fly.io/docs/mpg/)
