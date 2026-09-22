---
name: flyio-common-errors
description: >-
  Diagnose Fly.io deployment, routing, health, Machine, volume, and private-network failures with evidence-first triage. Use when an app is unhealthy or a release stalls. Trigger with: "debug Fly deploy", "why is my Fly app down", "triage Fly Machine".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[app-environment-and-symptom]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flyio
  - troubleshooting
  - health-checks
  - machines
compatibility: 'Requires read access to the affected app, the relevant release identifier, and permission to inspect redacted configuration, health, Machine, and log evidence.'
---

# Fly.io Failure Triage

## Overview

Classify the failing layer before changing anything. Separate local build failures, release orchestration, Machine lifecycle, Fly Proxy routing, private DNS, volume placement, and application behavior so remediation does not destroy the evidence.

## Prerequisites

- App and environment identifiers plus incident start time
- Last known healthy release, image, configuration, and region placement
- Read-only access to health, Machine, release, volume, and log evidence

## Instructions

### Step 1: Freeze the incident window

Record the symptom, first observation, affected regions, recent release or secret changes, and the last known healthy revision.

### Step 2: Validate configuration and release identity

Compare the deployed image and rendered configuration with the intended release. Check process groups, ports, services, health paths, signals, and timeouts.

### Step 3: Inspect health and Machine lifecycle

Distinguish a failed health check from a Machine that is stopped, suspended, replacing, or repeatedly restarting. Preserve instance-version information.

### Step 4: Check routing and networking

Verify public allocation, Fly Proxy service configuration, listening address, target port, and private `.internal` DNS semantics. Remember that stopped Machines are absent from AAAA responses.

### Step 5: Check regional storage dependencies

Confirm that any attached volume exists in the same region and is mounted at the expected path. Treat a single volume as a single-host durability boundary.

### Step 6: Choose the smallest recovery

Prefer rollback, configuration correction, or one bounded Machine action over fleet-wide restart. Reconcile health and image state after recovery.

## Authentication

Use a read-only organization token for observation where possible. A deploy-capable identity can change code and therefore reach runtime secrets; keep diagnostic access separate from mutation authority and never paste tokens into incident records.

## Tool Discipline

Use Read and Grep to inspect application configuration, deployment evidence, provider documentation, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for an approved plan, configuration, implementation, test, or redacted receipt. Do not create, deploy, scale, restart, stop, suspend, destroy, rotate, revoke, expose, or migrate live Fly.io resources without explicit operator approval.

## Output

- Layered incident timeline and affected-resource map
- Redacted evidence matrix for config, release, health, Machine, network, and volume state
- Bounded recovery or escalation plan with rollback and verification criteria

Return the target organization, app, environment, region set, Machine or database identifiers, source-contract fingerprint, evidence, unresolved risks, rollback state, and final decision without exposing tokens, secrets, connection strings, or customer data.

## Examples

After a release, one region returns errors. The operator verifies the new image, finds the Machine started but failing its HTTP health path, confirms the process listens on the wrong port, rolls back that release, and records the configuration mismatch without restarting healthy regions.

## Error Handling

| Failure | Response |
| --- | --- |
| Evidence is incomplete | Do not guess; identify the missing read surface, owner, and safe collection step. |
| Machine state oscillates | Capture current and version state, logs, exit information, and health before attempting another restart. |
| Volume is unavailable | Stop destructive deployment actions and verify region, attachment, snapshot, and restore options. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [Health checks](https://fly.io/docs/reference/health-checks/)
- [Machine states](https://fly.io/docs/machines/machine-states/)
- [Private networking](https://fly.io/docs/networking/private-networking/)
- [Fly Volumes](https://fly.io/docs/volumes/)
