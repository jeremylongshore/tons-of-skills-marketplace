---
name: canva-reliability-patterns
description: 'Implement Canva reliability controls for transport failures, asynchronous jobs, token rotation, throttling, and dead letters. Use when preventing duplicate writes or recovering safely across timeouts and restarts. Trigger with: "Canva retries", "Canva circuit breaker", "recover Canva job".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[operation-and-failure-budget]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - reliability
  - operations
compatibility: 'Requires a durable operation ledger, current error contract, scoped queues, and explicit failure budgets.'
---

# Canva Reconciliation and Recovery

## Overview

Reliability begins with knowing whether an operation happened. Reconcile existing resources and jobs before replaying a mutation, and keep credential rotation outside generic request retries.

## Prerequisites

- Operation types, retry classifications, and duplicate impact
- Durable identity/job ledger and terminal-state contract
- Endpoint/user queues, time budgets, alert owner, and rollback

## Instructions

### Step 1: Classify operations

Use Read and Grep to label safe read, token exchange, mutating submission, job poll, webhook delivery, and cleanup. Define retriable errors per operation.

### Step 2: Persist before dispatch

Create one application operation record with tenant/resource authorization and intended effect before sending a mutating request.

### Step 3: Handle ambiguous failure

After timeout or connection loss, use returned or recoverable identity to query existing state. Never blindly recreate a design, export, upload, or autofill.

### Step 4: Poll bounded jobs

Apply exponential backoff with jitter to the same job, stop at local deadline, continue later from durable state, and handle success/failed plus unknown future states safely.

### Step 5: Serialize credential refresh

Single-flight by Canva user, atomically store the returned replacement refresh token, wake waiting requests on success, and reauthorize rather than looping invalid credentials.

### Step 6: Use scoped circuits and dead letters

Open by endpoint/failure class, preserve operations with reconciliation state, and require an owner before replay. Do not mix authorization failures with provider availability.

### Step 7: Prove recovery

Use Write or Edit to test restart, duplicate delivery, lost response, throttling, terminal failure, refresh race, circuit recovery, and dead-letter replay.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

A network timeout follows export submission. The worker retains the operation and job reference, resumes polling after restart, and never submits a second export merely because the response was uncertain.

## Error Handling

| Failure | Response |
| --- | --- |
| No identity survived timeout | Stop automatic replay and investigate manually |
| Refresh token was reused | Require reauthorization and fix atomic rotation |
| Circuit hides authorization errors | Split failure classes and deny affected requests |
| Dead letter lacks owner/state | Do not replay it |

## Resources

- [First-party source notes](references/official-docs.md)
- [API request model](https://www.canva.dev/docs/connect/api-requests-responses/)
- [Authentication](https://www.canva.dev/docs/connect/authentication/)
