---
name: vastai-prod-checklist
description: >-
  Analyze readiness and issue a production go/no-go decision for a Vast.ai renter workload using retained evidence for cost, capacity, security, recovery, observability, and teardown. Use when a release needs production approval. Trigger with: "approve Vast.ai production", "run the Vast.ai launch checklist", "is this Vast.ai workload production ready".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[release-id-workload-and-slo]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - production
  - readiness
  - governance
compatibility: 'Requires an immutable release candidate, approved Vast.ai account, workload SLOs, security policy, and rollback owner.'
---

# Vast.ai Production Go/No-Go

## Overview

Production approval is an evidence bundle, not a list of optimistic assertions. Every gate needs an owner, artifact, and expiry; any failed critical gate yields NO-GO.

## Prerequisites

- Release ID, image digest, dataset/model identity, and expected traffic or job profile
- Capacity, latency, reliability, recovery, security, and spend objectives
- Named incident, billing, data-recovery, and teardown owners

## Instructions

### Step 1: Verify account and permissions

Confirm account/team context, positive balance or approved autobilling, least-privilege keys, audit visibility, and no credential in release artifacts.

### Step 2: Verify capacity policy

Demonstrate compliant offers or Serverless worker capacity across required GPU, VRAM, geography, reliability, and price constraints.

### Step 3: Verify immutable execution

Pin image/template/model identity and prove startup, health, output contract, and workload-specific acceptance on a canary.

### Step 4: Verify recovery

Restore from an external checkpoint or roll back a Serverless template. Prove that stop, outbid, offline, expiry, and zero-balance paths have owners.

### Step 5: Verify operations

Show bounded retries, terminal-state handling, logs/metrics, signed webhook or polling coverage, cost alarms, and escalation contacts.

### Step 6: Issue the decision

Record PASS, FAIL, owner, evidence URI, and expiry for each gate. Launch only on GO; retain the exact rollback and cleanup commands.

## Authentication

Production keys must be named and scoped by function. Separate billing, team administration, deployment, workload storage, and monitoring authority.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Per-gate PASS/FAIL matrix with evidence and expiry
- GO or NO-GO decision with accepted residual risks
- Rollback, incident, billing, and teardown owner receipt

Return release ID, account context, immutable identities, gate results, decision, approvers, expiry, and rollback target.

## Examples

A Serverless model release receives GO only after canary output parity, bounded scale testing, signed webhook acceptance, cost thresholds, and reverse rolling-update evidence are attached.

## Error Handling

| Failure | Response |
| --- | --- |
| Critical evidence is missing | Issue NO-GO; an owner assertion is not a substitute. |
| Offer capacity is temporarily absent | Delay or use an approved alternate profile; do not weaken policy silently. |
| Rollback was not exercised | Run it on the canary before production approval. |
| Billing owner is unavailable | Issue NO-GO because zero balance can stop workloads and endanger data. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Vast.ai pricing](https://docs.vast.ai/guides/pricing)
- [Manage instances](https://docs.vast.ai/guides/instances/manage-instances)
- [Notification webhooks](https://docs.vast.ai/guides/reference/notification-webhooks)
