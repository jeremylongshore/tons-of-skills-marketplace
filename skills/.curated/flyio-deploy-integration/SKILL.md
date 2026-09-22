---
name: flyio-deploy-integration
description: >-
  Plan a Fly.io rolling, canary, or blue-green release with health, capacity, storage, and rollback constraints. Use when a release needs progressive exposure. Trigger with: "canary deploy on Fly", "use Fly blue-green", "design Fly rollout".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[app-release-and-strategy]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flyio
  - progressive-delivery
  - canary
  - blue-green
compatibility: 'Requires a Fly Launch app, immutable image, configured health checks, sufficient temporary capacity, and an approved deployment and rollback owner.'
---

# Fly.io Progressive Deployment Design

## Overview

Select a provider-supported deployment strategy based on state, volume attachment, temporary capacity, and risk. Do not implement a custom traffic switch when Fly Launch already provides rolling, canary, blue-green, and immediate strategies with defined constraints.

## Prerequisites

- Immutable candidate and previous image references
- Healthy baseline Machines and at least one meaningful service health check
- State and volume inventory plus temporary capacity and cost approval

## Instructions

### Step 1: Classify the workload

Identify stateless and stateful process groups, attached volumes, singleton regions, release commands, connection draining, and external dependencies.

### Step 2: Choose a supported strategy

Use rolling for the general case. Canary creates one new Machine then rolls forward; blue-green creates replacement capacity in each region. Immediate is an emergency option with explicit downtime risk.

### Step 3: Validate strategy constraints

Reject canary or blue-green for Machines with attached volumes. Ensure blue-green has health checks and enough quota and capacity; account for `max-per-region` behavior.

### Step 4: Define acceptance gates

Set health, error, latency, saturation, business, and data-reconciliation thresholds with an observation window and named approver.

### Step 5: Execute one release owner

Pin image and config, serialize the release, observe Machine replacement and health, and prevent unrelated scaling or secret changes during the window.

### Step 6: Promote or reverse

Confirm every region and process group runs the intended image. If a gate fails, stop progression and restore the recorded prior release or configuration.

## Authentication

Use a scoped deploy token whose app and expiry match the rollout. Keep observation separate with read-only access where practical. Never embed the token in `fly.toml`, image layers, release metadata, or health-check output.

## Tool Discipline

Use Read and Grep to inspect application configuration, deployment evidence, provider documentation, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for an approved plan, configuration, implementation, test, or redacted receipt. Do not create, deploy, scale, restart, stop, suspend, destroy, rotate, revoke, expose, or migrate live Fly.io resources without explicit operator approval.

## Output

- Strategy decision with workload and volume constraints
- Capacity, health, observation, promotion, and rollback gates
- Per-region release and image reconciliation receipt

Return the target organization, app, environment, region set, Machine or database identifiers, source-contract fingerprint, evidence, unresolved risks, rollback state, and final decision without exposing tokens, secrets, connection strings, or customer data.

## Examples

A stateless service with two Machines per region and HTTP health checks uses blue-green. The operator confirms no volumes, approves temporary doubled capacity, observes all new Machines healthy, verifies the image digest, and only then allows old Machines to be destroyed.

## Error Handling

| Failure | Response |
| --- | --- |
| Strategy is incompatible with a volume | Switch to rolling or redesign persistence; do not force canary or blue-green. |
| New capacity cannot be placed | Stop before destroying old Machines and reassess region capacity or strategy. |
| Health passes but business gate fails | Treat the release as failed and reverse using the pinned previous image. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [Deploy strategies](https://fly.io/docs/launch/deploy/)
- [Health checks](https://fly.io/docs/reference/health-checks/)
