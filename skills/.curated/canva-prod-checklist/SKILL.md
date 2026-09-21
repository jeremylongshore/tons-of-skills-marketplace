---
name: canva-prod-checklist
description: 'Gate a Canva Connect release on authorization, review eligibility, data controls, async recovery, observability, and rollback evidence. Use when promoting a backend integration or enabling a new Canva operation. Trigger with: "Canva production checklist", "release Canva integration", "Canva go-live review".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[release-id-and-environment]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - production
  - operations
compatibility: 'Requires an exact release artifact, controlled production integration, current feature-status evidence, and rollback authority.'
---

# Canva Production Readiness Gate

## Overview

Make go-live an evidence decision tied to an immutable artifact. Preview features, broad scopes, unsafe callback hosts, ambiguous jobs, or unverifiable rollback keep the release closed.

## Prerequisites

- Release digest, configuration version, owner, and change scope
- Production integration, exact redirects, explicit scopes, and feature statuses
- Test receipts, migrations, observability, data policy, incident plan, and rollback

## Instructions

### Step 1: Verify identity and trust

Use Read and Grep to confirm exact artifact, environment, integration ID, callback hosts, backend-only secrets, CI event boundaries, and operator ownership.

### Step 2: Verify authorization

Review minimum explicit scopes, tenant/resource checks, capabilities, consent changes, disconnect cleanup, and token-refresh serialization.

### Step 3: Verify provider contracts

Pin current OpenAPI/changelog, identify deprecated and preview APIs, and confirm public-review eligibility. Canva states public integrations using preview features cannot pass review.

### Step 4: Verify operations

Prove operation identity, bounded retry, endpoint/user queueing, async job reconciliation, webhook idempotency if used, and partial-failure cleanup.

### Step 5: Verify data and telemetry

Prove content/credential classification, retention/deletion, URL handling, log redaction, low-cardinality metrics, alert ownership, and debug-bundle expiry.

### Step 6: Exercise failure and rollback

Use Write or Edit to record mocked failures, protected read-only integration proof, migration recovery, rollback command/path, and post-rollback reconciliation.

### Step 7: Approve or refuse

Record exact evidence, approver, residual risks, and activation steps. Refuse if any required fact is inferred rather than proven.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

A public release using a preview webhook path is refused. The team ships the non-preview core after exact-head tests and keeps the preview feature in a separate non-public experiment.

## Error Handling

| Failure | Response |
| --- | --- |
| Preview status is unclear | Treat the feature as ineligible until confirmed |
| Rollback was not exercised | Do not approve production |
| Scope set exceeds features | Reduce scopes and obtain new consent where required |
| Health proof mutates content | Replace it with a protected non-mutating read |

## Resources

- [First-party source notes](references/official-docs.md)
- [Creating integrations](https://www.canva.dev/docs/connect/creating-integrations/)
- [Connect security](https://www.canva.dev/docs/connect/guidelines/security/)
