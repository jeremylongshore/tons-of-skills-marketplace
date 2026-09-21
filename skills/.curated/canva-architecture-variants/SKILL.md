---
name: canva-architecture-variants
description: 'Choose a Canva Connect integration architecture from explicit trust, workload, and recovery constraints. Use when deciding between a backend monolith, service plus workers, or isolated multi-tenant services. Trigger with: "design Canva architecture", "scale Canva integration", "choose Canva topology".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[constraints-and-scale-profile]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - architecture
  - operations
compatibility: 'Architecture choices require a backend web application because Canva Connect secrets cannot be secured in browser-only clients.'
---

# Canva Architecture Decision

## Overview

Select the smallest topology that preserves backend OAuth, per-user token isolation, asynchronous job reconciliation, and policy-controlled data handling. Treat scale thresholds as measured local evidence, not Canva product limits.

## Prerequisites

- Expected operations, traffic shape, tenants, and recovery objectives
- Data classification, retention policy, and secret backend
- Current scopes, capabilities, preview dependencies, and deployment constraints

## Instructions

### Step 1: Map trust boundaries

Identify browser, backend, token store, job ledger, worker, data store, and Canva API boundaries. Mark every place customer content or credentials could cross.

### Step 2: Choose the base shape

Use a backend monolith for one bounded service, a service plus worker when asynchronous jobs must outlive requests, or isolated services only when ownership and failure domains justify them.

### Step 3: Design token rotation

Serialize refresh per Canva user, atomically replace the single-use refresh token, and separate access-token and refresh-token storage.

### Step 4: Design job reconciliation

Persist opaque job identity before dispatch, poll with bounded backoff, and reconcile terminal state before repeating a mutating operation.

### Step 5: Design policy enforcement

Resolve tenant, resource, explicit scope, capability, preview status, and data policy before dispatch rather than inside a generic HTTP client.

### Step 6: Record the decision

Use Write or Edit to capture selected shape, rejected alternatives, assumptions, failure modes, rollback, and validation evidence.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

A service exports designs asynchronously for multiple tenants. A backend owns OAuth and policy, a durable ledger owns job identity, and workers are partitioned by tenant without embedding user IDs in metrics.

## Error Handling

| Failure | Response |
| --- | --- |
| Browser-only design proposed | Reject it because client secrets and token exchange require a backend |
| Workers can double-submit | Add durable identity and reconciliation before scaling |
| Topology chosen by guessed volume | Measure queue and failure behavior first |
| Preview dependency blocks review | Separate or disable that feature for the public release |

## Resources

- [First-party source notes](references/official-docs.md)
- [Connect security](https://www.canva.dev/docs/connect/guidelines/security/)
- [Authentication](https://www.canva.dev/docs/connect/authentication/)
