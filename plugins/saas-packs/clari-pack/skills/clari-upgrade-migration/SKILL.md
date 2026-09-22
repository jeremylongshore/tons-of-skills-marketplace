---
name: clari-upgrade-migration
description: >-
  Migrate a Clari integration across hosts, versions, endpoint contracts, or export schemas with dual-read comparison and rollback. Use when retiring legacy clients or mappings. Trigger with: "upgrade Clari API", "migrate a Clari client", "handle Clari schema drift".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[current-contract-target-contract-and-dataset]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - clari
  - migration
  - api-versioning
  - schema-evolution
compatibility: 'Requires current and target contract fingerprints, representative non-production data, a compatibility mapping, and a retained rollback path.'
---

# Clari API and Schema Migration

## Overview

Treat provider URL, authentication, request schema, job behavior, response schema, and destination mapping as one versioned contract. Prove the target alongside the current path before moving production traffic or published data.

## Prerequisites

- Current and target hosts, versions, operations, schemas, and credential types
- Representative requests and expected reconciliations
- Dual-run environment, migration owner, and rollback deadline

## Instructions

### Step 1: Inventory the delta

Diff hosts, base paths, auth headers, methods, fields, enum values, errors, limits, pagination, and mutation semantics.

### Step 2: Build an explicit mapping

Classify every used field and behavior as unchanged, renamed, transformed, added, removed, or unsupported.

### Step 3: Update clients and fixtures

Pin the target contract, add target adapters and schemas, and retain current fixtures for regression and rollback testing.

### Step 4: Dual-read safely

Run bounded non-production or approved parallel reads for identical windows and compare identifiers, counts, values, states, and latency.

### Step 5: Cut over atomically

Move one workload or consumer at a time, retain the prior client and published snapshot, and stop on unexplained divergence.

### Step 6: Retire with evidence

After the rollback window, remove legacy credentials and routes, update runbooks, and retain the comparison and revocation receipts.

## Authentication

Do not reuse headers merely because two surfaces belong to Clari. Revenue, v2 ingestion, and Copilot each require their documented host and credentials; rotate or revoke legacy credentials only after rollback is no longer needed.

## Tool Discipline

Use Read and Grep to inspect configuration, provider contracts, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not issue, rotate, revoke, create, update, cancel, delete, export, ingest, or publish provider data without explicit operator approval.

## Output

- Contract delta and field-level compatibility map
- Dual-read reconciliation and performance report
- Cutover, rollback-window, legacy revocation, and retirement receipt

Return the exact surface, environment, resource or job identifiers, contract fingerprint, evidence, unresolved risks, and final decision without exposing credentials or sensitive customer data.

## Examples

A client moves from an old Copilot host to `rest-api.copilot.clari.com`, validates the two-header authentication contract, dual-reads one approved week, reconciles call IDs, then revokes the legacy credential after the rollback window.

## Error Handling

| Failure | Response |
| --- | --- |
| Target omits a required field | Stop cutover and define a supported replacement or consumer change. |
| Dual-read values diverge | Classify window, scope, schema, and timing differences before accepting the target. |
| Legacy credential is revoked early | Restore from the approved overlap credential or pause until a safe rollback path exists. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Clari Revenue API reference](https://developer.clari.com/default/documentation/external_spec)
- [Clari Copilot API reference](https://api-doc.copilot.clari.com/)
