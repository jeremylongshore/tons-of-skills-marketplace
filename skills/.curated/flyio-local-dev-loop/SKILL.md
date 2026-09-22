---
name: flyio-local-dev-loop
description: >-
  Build a repeatable local Fly.io development loop with containers, config validation, private-service access, and disposable remote verification. Use when aligning local behavior with Fly Machines. Trigger with: "develop Fly app locally", "proxy Fly database", "test fly.toml before deploy".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[app-service-and-dev-environment]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flyio
  - local-development
  - containers
  - proxy
compatibility: 'Requires application source, a local container runtime where used, read access to a development Fly.io app, and explicit approval before connecting to remote data.'
---

# Fly.io Local-to-Remote Development Loop

## Overview

Keep local unit and container checks separate from provider integration checks. Use synthetic fixtures by default, validate configuration before deployment, and treat `fly proxy` or WireGuard access to a remote service as production-adjacent even when initiated from a laptop.

## Prerequisites

- Local build and test commands plus expected runtime port
- Development-only app or isolated process group and disposable test data
- Approved remote-service access path with data handling and teardown rules

## Instructions

### Step 1: Define the parity contract

Record runtime image, architecture, process command, port, environment names, health route, filesystem expectations, and provider-only dependencies.

### Step 2: Build and test locally

Use deterministic dependencies and synthetic fixtures. Exercise startup, health, shutdown, migration, and failure paths without Fly.io credentials.

### Step 3: Validate configuration separately

Review `fly.toml` against the app contract, including process groups, services, checks, signals, resources, and mounts. Keep secrets out of the file.

### Step 4: Connect to remote services narrowly

If remote access is necessary, target a development service through an approved proxy or WireGuard path, bind locally, limit time, and never copy remote data into fixtures.

### Step 5: Deploy to a disposable boundary

Use a dedicated development app or temporary Machine, immutable image, modest resource size, and clear expiry. Do not reuse the production app as a test target.

### Step 6: Reconcile and tear down

Compare local and remote health, logs, architecture, and timing; capture differences, then stop or remove approved disposable resources.

## Authentication

Use an interactive operator session or a development-app token with no production scope. Database credentials remain in the secret manager and are injected only for the bounded session. Close proxies and revoke temporary access after use.

## Tool Discipline

Use Read and Grep to inspect application configuration, deployment evidence, provider documentation, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for an approved plan, configuration, implementation, test, or redacted receipt. Do not create, deploy, scale, restart, stop, suspend, destroy, rotate, revoke, expose, or migrate live Fly.io resources without explicit operator approval.

## Output

- Local/remote parity matrix and fixture inventory
- Reviewed development configuration and access plan
- Disposable integration receipt with results, differences, costs, and teardown state

Return the target organization, app, environment, region set, Machine or database identifiers, source-contract fingerprint, evidence, unresolved risks, rollback state, and final decision without exposing tokens, secrets, connection strings, or customer data.

## Examples

A developer tests the container and health route locally with synthetic data, validates `fly.toml`, opens a time-bounded proxy to a development database, runs a read-only schema check, deploys to a disposable app, and removes the app after reconciliation.

## Error Handling

| Failure | Response |
| --- | --- |
| Local container passes but remote fails | Compare architecture, listening address, filesystem, environment names, health timing, and remote builder output. |
| Proxy exposes the service broadly | Stop it, bind to the approved local interface and port, rotate if necessary, and record the exposure. |
| Disposable app remains billable | Escalate to the owner and remove it only after confirming no data or rollback dependency. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [fly proxy](https://fly.io/docs/flyctl/proxy/)
- [Private networking](https://fly.io/docs/networking/private-networking/)
