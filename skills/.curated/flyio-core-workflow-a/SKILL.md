---
name: flyio-core-workflow-a
description: >-
  Operate a Fly.io application release from configuration review through deploy, scale, secret change, and rollback. Use when shipping or changing a Fly Launch app. Trigger with: "deploy Fly app", "scale Fly Machines", "roll back Fly release".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[app-environment-and-release]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flyio
  - deployments
  - scaling
  - secrets
compatibility: 'Requires an existing Fly.io organization, an approved app target, a deploy-capable scoped identity, and a tested health and rollback contract.'
---

# Fly.io Application Release Lifecycle

## Overview

Treat the app release as a state transition with explicit configuration, image, capacity, health, and rollback boundaries. Fly Launch manages Machines from `fly.toml`, but production success still requires reconciliation against the running fleet.

## Prerequisites

- Source revision, image build contract, app name, environment, and primary region
- Reviewed `fly.toml` with process groups, services, health checks, and shutdown settings
- Approved deploy strategy, capacity envelope, secret plan, and rollback target

## Instructions

### Step 1: Inventory the current app

Record current release, running image, Machine counts and regions, health, IP allocation, secrets digests, and attached storage.

### Step 2: Render the desired state

Review build, process groups, services, concurrency, autostart or autostop, VM resources, regions, mounts, release command, and deployment policy.

### Step 3: Stage secrets separately

Use Fly secrets rather than plaintext `[env]` values. Decide whether a secret change should restart Machines immediately or be staged for the release.

### Step 4: Select the deployment strategy

Use rolling by default. Use canary only when temporary extra capacity is valid and no Machine volume blocks it; use blue-green only with health checks and compatible stateless capacity.

### Step 5: Deploy and wait

Bind the release to an immutable image, observe replacement, and wait for health and Machine convergence. Do not infer success from image push alone.

### Step 6: Reconcile or roll back

Compare desired and actual image, count, regions, health, and service behavior. Roll back if acceptance criteria or error budgets fail.

## Authentication

Use an app-scoped deploy token for a single app and a short-lived organization token only when the operation legitimately spans apps. Fly App secrets are encrypted at rest but become environment variables inside Machines; anyone with deploy access can deploy code that reads them.

## Tool Discipline

Use Read and Grep to inspect application configuration, deployment evidence, provider documentation, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for an approved plan, configuration, implementation, test, or redacted receipt. Do not create, deploy, scale, restart, stop, suspend, destroy, rotate, revoke, expose, or migrate live Fly.io resources without explicit operator approval.

## Output

- Preflight snapshot and desired-state review
- Release plan with strategy, capacity, health, and rollback gates
- Post-release reconciliation receipt or rollback record

Return the target organization, app, environment, region set, Machine or database identifiers, source-contract fingerprint, evidence, unresolved risks, rollback state, and final decision without exposing tokens, secrets, connection strings, or customer data.

## Examples

A stateless API with two healthy Machines uses a rolling release. The operator stages one secret, pins the image digest, deploys one Machine at a time, verifies the health endpoint and image on both Machines, and closes only after the previous image remains available for rollback.

## Error Handling

| Failure | Response |
| --- | --- |
| Release command fails | Stop the release, retain its logs, and fix the migration or command contract before retrying. |
| Replacement cannot become healthy | Preserve the failed Machine evidence and roll back rather than widening unavailable capacity. |
| Desired and actual fleet differ | Re-read current state, identify an interrupted or concurrent change, and reconcile under one release owner. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [Deploy an app](https://fly.io/docs/launch/deploy/)
- [App secrets](https://fly.io/docs/apps/secrets/)
- [Health checks](https://fly.io/docs/reference/health-checks/)
