---
name: canva-reference-architecture
description: 'Implement a Canva Connect backend reference architecture with policy, OAuth, job reconciliation, and privacy-safe operations. Use when establishing service boundaries, ownership, storage, and recovery for production. Trigger with: "Canva reference architecture", "design Canva backend", "Canva service layout".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[requirements-and-data-classification]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - architecture
  - operations
compatibility: 'Requires a backend web application, durable token/job storage, approved data policy, and service ownership.'
---

# Canva Production Reference Architecture

## Overview

Separate browser experience, backend OAuth/policy, provider adapter, durable operation ledger, workers, and controlled data stores. The architecture must prevent cross-tenant access and duplicate mutation by construction.

## Prerequisites

- Operations, tenants, traffic, data classes, and recovery objectives
- Scopes, capabilities, preview dependencies, and public-review posture
- Secret/token store, operation ledger, queue, observability, and rollback platform

## Instructions

### Step 1: Draw trust boundaries

Map browser, callback, backend, policy service, token vault, Canva adapter, job ledger, worker queue, data store, telemetry, and provider edges.

### Step 2: Own authorization centrally

Resolve authenticated tenant, application role, resource ownership, explicit scope, capability, feature status, and data purpose before the adapter.

### Step 3: Own tokens separately

Keep client secret and tokens backend-only, encrypt access and refresh tokens separately, serialize per-user refresh, and atomically replace single-use refresh tokens.

### Step 4: Own mutation identity

Create a durable operation record before provider dispatch, attach returned resource/job identity, and reconcile terminal state across retries and restarts.

### Step 5: Own data lifecycle

Store minimum approved metadata/content, authorize every read, expire temporary references, implement consent/account deletion, and keep protected values out of telemetry.

### Step 6: Own failure recovery

Use endpoint-scoped admission, bounded retries, dead letters with reconciliation state, feature flags, immutable deploys, and exercised rollback.

### Step 7: Record the blueprint

Use Write or Edit to document responsibilities, interfaces, schemas, threat decisions, SLOs, failure modes, and verification evidence.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

The browser never receives a client secret or refresh token. The backend policy service authorizes an export, the ledger preserves identity, a worker polls the same job, and the application mediates result delivery.

## Error Handling

| Failure | Response |
| --- | --- |
| Business roles leak into generic client | Move authorization before the adapter |
| Refresh can run concurrently | Add a per-user lock and atomic replacement |
| Queue lacks operation identity | Stop writes until the ledger exists |
| Telemetry contains resource identifiers | Redesign dimensions and redact |

## Resources

- [First-party source notes](references/official-docs.md)
- [Authentication](https://www.canva.dev/docs/connect/authentication/)
- [API request model](https://www.canva.dev/docs/connect/api-requests-responses/)
