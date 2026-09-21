---
name: canva-migration-deep-dive
description: 'Plan and execute a staged migration into or across Canva Connect application boundaries. Use when replacing a legacy design provider, moving token or job infrastructure, or introducing new Canva API surfaces. Trigger with: "migrate to Canva", "Canva strangler migration", "move Canva integration".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[source-contract-and-rollout-window]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - migration
  - operations
compatibility: 'Requires source/target contracts, content rights, user-consent analysis, rollback authority, and a bounded migration cohort.'
---

# Canva Integration Migration Program

## Overview

Separate provider-contract, credential, application-data, and user-experience migrations. Preserve reversibility and reconcile every asynchronous or mutating operation before moving the next cohort.

## Prerequisites

- Source and target operation/capability matrix
- Data inventory, rights, retention, consent, and identifier map
- Cohort plan, feature flag, validation sample, rollback, and owner

## Instructions

### Step 1: Define parity honestly

Use Read and Grep to map supported, changed, preview, unavailable, and intentionally retired operations. Do not invent workarounds for unsupported provider behavior.

### Step 2: Design identity and consent

Keep Canva user/tenant identity separate from legacy IDs, request only explicit scopes, and identify when fresh user authorization is mandatory.

### Step 3: Design data movement

Classify assets, designs, metadata, comments, and references; validate rights and format before transfer; avoid copying content that lacks an approved purpose.

### Step 4: Build dual-path evidence

Use Write or Edit to add contract tests, operation identity, reconciliation, comparison receipts, and a feature-flagged target path without duplicating writes.

### Step 5: Migrate a small cohort

Choose approved synthetic or low-risk users, enforce rate/admission controls, verify each result, and stop on authorization, data, or parity drift.

### Step 6: Roll forward or back

Advance only from measured evidence. Roll back routing without losing target-side job/resource identity, then reconcile and clean partial artifacts.

### Step 7: Close the legacy path

After the retention and rollback window, revoke unused credentials, delete approved stale data, remove old routes, and preserve a content-free audit receipt.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

A legacy export path is replaced cohort by cohort. The application compares contract outcomes, routes one authorized cohort to Canva, and retains enough opaque identity to roll back and reconcile without double creation.

## Error Handling

| Failure | Response |
| --- | --- |
| Feature parity is missing | Document it and defer or retire the use case |
| Identifier mapping is ambiguous | Stop migration for the affected records |
| Dual path can double-write | Add single authoritative routing and operation identity |
| Rollback loses target jobs | Persist and reconcile them before proceeding |

## Resources

- [First-party source notes](references/official-docs.md)
- [API versions](https://www.canva.dev/docs/connect/versions/)
- [Latest OpenAPI](https://www.canva.dev/sources/connect/api/latest/api.yml)
