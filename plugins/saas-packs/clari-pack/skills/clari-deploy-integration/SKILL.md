---
name: clari-deploy-integration
description: >-
  Deploy a single-writer Clari scheduler with durable job state, atomic publication, observability, and rollback. Use when productionizing recurring Revenue or Copilot extraction. Trigger with: "deploy a Clari pipeline", "schedule Clari exports", "ship Clari integration".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[orchestrator-cadence-and-destination]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - clari
  - deployment
  - scheduler
  - data-pipeline
compatibility: 'Requires an approved orchestrator, secret manager, durable state store, destination, capacity plan, and rollback environment.'
---

# Deploy a Clari Scheduled Data Pipeline

## Overview

Deploy orchestration rather than embedding long-running polling in ephemeral request handlers. Ensure one logical scheduler owns each workload, persists provider job IDs or cursors before waiting, and separates landing from publication.

## Prerequisites

- Versioned container or runtime artifact and infrastructure manifest
- Per-surface credential references and least-privilege identity
- Durable checkpoint store, encrypted landing zone, and atomic publish mechanism

## Instructions

### Step 1: Package the worker

Pin dependencies and contract fingerprints, run as a non-root identity, and expose no inbound endpoint unless operationally required.

### Step 2: Inject configuration

Supply base URLs, credential references, forecast or workspace scope, cadence, limits, destination, and retention through managed configuration.

### Step 3: Enforce single-writer scheduling

Use a lease or platform concurrency rule so overlapping invocations cannot queue duplicate exports or replay mutations.

### Step 4: Persist before polling

Write the request fingerprint and returned job ID or Copilot cursor durably before any wait, retry, or process exit.

### Step 5: Publish through gates

Land, validate, reconcile, and atomically advance the destination only after the provider operation and local checks succeed.

### Step 6: Roll out and roll back

Canary one bounded workload, compare service levels and data, then promote; retain the prior artifact and checkpoint reader for reversal.

## Authentication

Mount only the credentials needed by the selected surface and environment. Prevent secret values and provider payloads from entering process arguments, deployment diffs, health endpoints, or logs.

## Tool Discipline

Use Read and Grep to inspect configuration, provider contracts, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not issue, rotate, revoke, create, update, cancel, delete, export, ingest, or publish provider data without explicit operator approval.

## Output

- Immutable deployment artifact and configuration manifest
- Scheduler ownership, lease, checkpoint, and retry policy
- Canary comparison and production promote or rollback receipt

Return the exact surface, environment, resource or job identifiers, contract fingerprint, evidence, unresolved risks, and final decision without exposing credentials or sensitive customer data.

## Examples

An orchestrator runs one quarterly forecast export at a time, persists the Clari job ID, resumes polling after a restart, validates the landing file, and atomically advances the warehouse snapshot.

## Error Handling

| Failure | Response |
| --- | --- |
| Two schedulers overlap | Acquire a distributed lease before provider calls and stop the losing worker. |
| Worker dies after queuing | Resume from the persisted job ID instead of submitting another export. |
| Canary data regresses | Keep the prior deployment and published snapshot, disable the candidate, and preserve evidence. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Clari Revenue API reference](https://developer.clari.com/default/documentation/external_spec)
- [Clari Copilot API reference](https://api-doc.copilot.clari.com/)
- [Clari service status](https://clari.statuspage.io/)
