---
name: canva-incident-runbook
description: 'Analyze and contain a Canva Connect incident with evidence-led recovery. Use when authentication, design, export, asset, webhook, or provider failures affect users. Trigger with: "Canva incident", "Canva outage", "triage Canva production".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[incident-id-and-symptoms]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - incident
  - operations
compatibility: 'Requires incident authority, approved read-only diagnostics, service ownership, and rollback access.'
---

# Canva Incident Response

## Overview

Contain impact before debugging deeply. Distinguish provider status, application release/config, tenant authorization, endpoint throttling, async-job backlog, and preview drift.

## Prerequisites

- Incident ID, severity policy, affected operations, and UTC window
- Current deployment/config revisions and last known good
- Approved test user, rollback owner, and communications channel

## Instructions

### Step 1: Declare and bound

Record start time, reporter, user-visible symptom, affected tenants/operations, suspected data exposure, and current severity without copying customer content.

### Step 2: Contain

Pause only unsafe mutations, refresh races, or affected queues. Preserve existing job identity and keep safe read-only paths available when policy permits.

### Step 3: Check broad signals

Use Read and Grep to compare deployment/config changes, error/status trends, queue age, authorization failures, and Canva's official status/changelog.

### Step 4: Run a minimal probe

Use an approved test user for one non-mutating endpoint. Never infer global provider health from a single production user.

### Step 5: Mitigate and reconcile

Roll back the responsible release/config, reduce endpoint concurrency, disable a changed preview path, or reauthorize only affected users based on evidence. Reconcile queued jobs before resuming.

### Step 6: Close with proof

Use Write or Edit to record timeline, decisions, impact, data assessment, recovery evidence, remaining jobs, rollback result, and preventive owner.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

After a release, one tenant sees export failures while other reads succeed. The operator pauses that tenant's export queue, rolls back the adapter, reconciles existing jobs, and avoids declaring a Canva-wide outage.

## Error Handling

| Failure | Response |
| --- | --- |
| Provider and app evidence conflict | Keep both hypotheses open and collect another independent signal |
| Potential credential exposure | Contain and rotate through the credential owner immediately |
| Queued writes are ambiguous | Do not resume until each operation is reconciled |
| Rollback does not recover | Escalate with the redacted failure bundle |

## Resources

- [First-party source notes](references/official-docs.md)
- [Canva status](https://www.canvastatus.com/)
- [Error responses](https://www.canva.dev/docs/connect/error-responses/)
