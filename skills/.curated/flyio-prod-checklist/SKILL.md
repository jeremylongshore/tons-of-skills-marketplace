---
name: flyio-prod-checklist
description: >-
  Gate a Fly.io production release across ownership, configuration, identity, health, capacity, data, observability, cost, and rollback. Use when reviewing a first launch or material change. Trigger with: "review Fly production readiness", "approve Fly launch", "run Fly go-live checklist".
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
  - production-readiness
  - reliability
  - go-live
compatibility: 'Requires an approved production app, accountable owners, service objectives, a scoped deploy identity, and evidence from a representative non-production release.'
---

# Fly.io Production Readiness Gate

## Overview

Make go-live a signed evidence boundary. The gate must cover the actual workload: stateless Machines, region-bound volumes, Managed Postgres, release commands, health semantics, autostart, networking, observability, billing, and tested rollback.

## Prerequisites

- Business, technical, security, data, support, and rollback owners
- Immutable candidate image and reviewed configuration
- Load, failure, restore, deployment, and rollback evidence from a representative environment

## Instructions

### Step 1: Confirm ownership and scope

Record app, organization, environment, domains, regions, process groups, data stores, objectives, on-call route, and accepted risks.

### Step 2: Review identity and secrets

Use scoped expiring tokens, protect production environments, inspect secret names and digests without values, and prove rotation and revocation.

### Step 3: Review runtime and deployment

Validate image, architecture, ports, processes, signals, release command, health checks, strategy, unavailable capacity, and volume compatibility.

### Step 4: Review resilience and data

Confirm Machine redundancy where required, regional placement, dependency failure behavior, Managed Postgres or volume backup boundaries, restore tests, and reconciliation.

### Step 5: Review observability and cost

Prove logs, metrics, health, alerts, provider-status escalation, resource inventory, cost owner, and cleanup of obsolete billable resources.

### Step 6: Exercise launch and rollback

Run the approved release path, observe acceptance gates, restore the prior image or config in a drill, and close only after actual fleet reconciliation.

## Authentication

Production deploy uses the narrowest app or organization token in a protected environment. Read-only monitoring should not share deploy authority. Remember that anyone with deploy access can deploy code that reads runtime App secrets.

## Tool Discipline

Use Read and Grep to inspect application configuration, deployment evidence, provider documentation, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for an approved plan, configuration, implementation, test, or redacted receipt. Do not create, deploy, scale, restart, stop, suspend, destroy, rotate, revoke, expose, or migrate live Fly.io resources without explicit operator approval.

## Output

- Signed production readiness decision with owners and exceptions
- Evidence index for identity, config, health, load, data recovery, observability, cost, and support
- Launch, rollback, and post-launch verification plan

Return the target organization, app, environment, region set, Machine or database identifiers, source-contract fingerprint, evidence, unresolved risks, rollback state, and final decision without exposing tokens, secrets, connection strings, or customer data.

## Examples

A web app with Managed Postgres passes only after the team proves two healthy Machines, scoped deploy and read-only tokens, a rolling deploy, database restore and reconnect, region-aware alerts, current cost ownership, and rollback to the previous image.

## Error Handling

| Failure | Response |
| --- | --- |
| Required evidence is missing | Keep the gate open and assign the exact proof, owner, and deadline. |
| Exception has no expiry | Reject it or add a compensating control, approver, review date, and rollback trigger. |
| Rollback drill fails | Do not approve go-live until image, config, secret, and data recovery paths are corrected. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [Health checks](https://fly.io/docs/reference/health-checks/)
- [Deploy an app](https://fly.io/docs/launch/deploy/)
- [Monitoring](https://fly.io/docs/monitoring/)
- [Managed Postgres](https://fly.io/docs/mpg/)
