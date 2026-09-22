---
name: vastai-incident-runbook
description: >-
  Analyze, diagnose, and recover a Vast.ai renter workload from outbid, exited, offline, scheduling, low-credit, or data-risk incidents while controlling billing and destructive actions. Use when a Vast.ai workload or account enters an incident state. Trigger with: "Vast.ai incident", "recover an offline Vast.ai job", "stop emergency Vast.ai spend".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[severity-resource-ids-and-last-good-checkpoint]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - incident-response
  - recovery
  - billing
compatibility: 'Requires affected resource IDs, read access, external checkpoints, incident authority, and a named billing owner.'
---

# Vast.ai Workload Recovery Runbook

## Overview

Protect people and credentials first, then preserve recoverable data, stop uncontrolled spend, and restore service from an external checkpoint or last-known-good template. Provider states imply different actions and must not be collapsed into retry.

## Prerequisites

- Severity, start time, affected instances/endpoints, release, and user impact
- Last verified external checkpoint or Serverless template
- Incident commander, data owner, billing owner, and authority for stop/destroy/rollback

## Instructions

### Step 1: Stabilize identity and scope

Confirm account/team context, affected IDs, current state, balance, and whether a credential or data exposure is involved.

### Step 2: Classify the provider state

Outbid/stopped may retain disk and storage charges; exited is workload failure; scheduling may await a reclaimed GPU; unknown/offline is host heartbeat loss; low credit threatens availability and data.

### Step 3: Preserve recovery evidence

Copy reachable artifacts and logs, record template/image identity, and verify the newest external checkpoint before any destroy.

### Step 4: Contain cost or exposure

Stop new creates, revoke compromised keys, and use stop or destroy only under the incident's data-versus-cost decision.

### Step 5: Restore on a clean target

Resume from the verified checkpoint on a compliant different offer, or roll Serverless back to the last-known-good template.

### Step 6: Reconcile and close

Confirm service and output, destroy superseded resources, audit charges, rotate temporary access, and document the gap and prevention action.

## Authentication

Use an incident key with the minimum temporary permissions and a short revocation deadline. Keep billing-write, team administration, workload storage, and control-plane authority separated.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- State-based incident timeline and containment decision
- Checkpoint/template recovery and service-validation evidence
- Resource cleanup, charge reconciliation, access rotation, and postmortem receipt

Return severity, IDs, state class, last good checkpoint/template, containment, restored target, data gap, spend impact, and closed resources.

## Examples

After a host goes offline, the team avoids blind restarts, restores the last external checkpoint on a different verified offer, validates output, and retains the original instance ID for support and billing reconciliation.

## Error Handling

| Failure | Response |
| --- | --- |
| No external checkpoint exists | State the recovery gap explicitly and attempt data salvage only if the host becomes reachable. |
| Balance is zero or negative | Escalate immediately; instances stop and resources may be at risk of deletion. |
| Destruction would erase the only data | Require the incident commander and data owner to make the containment decision. |
| Replacement also fails | Stop churn, compare common image/data/config factors, and escalate with redacted evidence. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Troubleshooting](https://docs.vast.ai/guides/reference/troubleshooting)
- [Billing and negative balances](https://docs.vast.ai/guides/reference/billing#negative-balances)
- [Manage instances](https://docs.vast.ai/guides/instances/manage-instances)
