---
name: flyio-hello-world
description: >-
  Prepare and verify a minimal Fly.io application launch with reviewable configuration and a safe first deployment. Use when onboarding a new service. Trigger with: "launch first Fly app", "deploy hello world to Fly", "create Fly launch plan".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[source-directory-app-and-region]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flyio
  - onboarding
  - fly-launch
  - deployment
compatibility: 'Requires a Fly.io account and organization, a containerizable application, an available app name, and approval to create billable resources.'
---

# First Fly.io App Launch

## Overview

Create the smallest useful first deployment while keeping generated configuration reviewable. Start with one environment, one explicit region, a health endpoint, and no persistent data; add global placement or storage only after the base release is observable and repeatable.

## Prerequisites

- Application source, runtime port, startup command, and local health proof
- Organization, app naming policy, region choice, and cost owner
- Interactive identity for setup or a scoped token for approved automation

## Instructions

### Step 1: Inspect the application

Identify build method, Dockerfile status, process command, listening address, internal port, health route, environment, and secret inputs.

### Step 2: Generate without deploying

Use the provider launch flow with deployment disabled so `fly.toml` and any Dockerfile changes can be reviewed before resource creation.

### Step 3: Review the config

Confirm app name, primary region, build source, process groups, service ports, health checks, VM size, autostart or autostop, and shutdown behavior.

### Step 4: Set secrets safely

Store runtime credentials through Fly App secrets. Leave non-sensitive configuration in reviewed environment fields and exclude local secret files from source control.

### Step 5: Perform the approved first deploy

Bind the source revision and image, use rolling behavior, and observe build, Machine creation, and health rather than assuming the public URL proves complete success.

### Step 6: Verify and document

Check the endpoint, health status, Machine image and region, logs, restart behavior, and billable resources. Record teardown or ownership before handoff.

## Authentication

Interactive onboarding can use `fly auth login`. Automation should use the narrowest expiring token exposed as `FLY_API_TOKEN` or `FLY_ACCESS_TOKEN`. Never copy the personal login token into CI.

## Tool Discipline

Use Read and Grep to inspect application configuration, deployment evidence, provider documentation, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for an approved plan, configuration, implementation, test, or redacted receipt. Do not create, deploy, scale, restart, stop, suspend, destroy, rotate, revoke, expose, or migrate live Fly.io resources without explicit operator approval.

## Output

- Reviewed Docker and `fly.toml` changes
- First-release plan with app, region, image, health, cost, and teardown boundaries
- Post-deploy receipt or clean rollback and resource-removal plan

Return the target organization, app, environment, region set, Machine or database identifiers, source-contract fingerprint, evidence, unresolved risks, rollback state, and final decision without exposing tokens, secrets, connection strings, or customer data.

## Examples

A small HTTP service listens on the configured internal port and exposes `/health`. The operator generates `fly.toml` without deploying, reviews one region and a modest VM size, sets one secret, deploys, verifies health and image identity, and assigns an owner.

## Error Handling

| Failure | Response |
| --- | --- |
| Generated config is surprising | Stop before deploy, compare with app runtime requirements, and edit only reviewed fields. |
| App name or region is unavailable | Choose from current provider responses and update the plan; do not assume global capacity. |
| First Machine is unhealthy | Preserve build and health evidence, correct the port or startup contract, and avoid repeated blind deploys. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [fly launch](https://fly.io/docs/flyctl/launch/)
- [Deploy an app](https://fly.io/docs/launch/deploy/)
- [Health checks](https://fly.io/docs/reference/health-checks/)
