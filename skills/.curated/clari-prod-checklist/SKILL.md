---
name: clari-prod-checklist
description: >-
  Analyze and gate a Clari integration for production with evidence for access, correctness, resilience, privacy, rollback, and ownership. Use when approving a launch or material change. Trigger with: "review Clari readiness", "approve Clari production", "run the Clari launch checklist".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[integration-release-and-environment]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - clari
  - production-readiness
  - release-gate
  - operations
compatibility: 'Requires a release candidate, non-production test evidence, named owners, and an approved production change window.'
---

# Clari Integration Production Readiness

## Overview

Convert production readiness into a fail-closed evidence bundle. A green decision requires proof of provider access, contract compatibility, data correctness, quota behavior, observability, security, recovery, and operator ownership.

## Prerequisites

- Versioned release candidate and endpoint inventory
- Completed non-production happy-path and failure-path tests
- Change owner, business owner, security owner, and rollback authority

## Instructions

### Step 1: Verify identity and contracts

Confirm surface-specific credentials, effective scope, base URL, API version, schema fingerprint, and entitlement.

### Step 2: Verify data correctness

Reconcile counts, identifiers, time periods, totals, pagination, and empty-result behavior against an approved source.

### Step 3: Verify resilience

Exercise timeout, 429, provider 5xx, aborted job, partial load, schema drift, and restart from checkpoint.

### Step 4: Verify security and privacy

Prove secret redaction, least privilege, encryption, retention, deletion, mutation gates, and sensitive-content minimization.

### Step 5: Verify operations

Confirm dashboards, alerts, service-status dependency, runbook, support bundle, capacity headroom, and on-call ownership.

### Step 6: Approve or reject

Record exact artifact hashes and approvers. Launch only when rollback is rehearsed and no required evidence is missing.

## Authentication

Production secrets must be injected from the approved manager into the matching client and never copied into release artifacts. Verify rotation and emergency revocation before launch.

## Tool Discipline

Use Read and Grep to inspect configuration, provider contracts, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not issue, rotate, revoke, create, update, cancel, delete, export, ingest, or publish provider data without explicit operator approval.

## Output

- Signed readiness matrix with evidence links and hashes
- Go/no-go decision with explicit exceptions, owners, and expiry
- Rollback trigger, procedure, and rehearsed result

Return the exact surface, environment, resource or job identifiers, contract fingerprint, evidence, unresolved risks, and final decision without exposing credentials or sensitive customer data.

## Examples

A forecast pipeline passes reconciliation and restart tests but lacks a verified token revocation drill. The launch remains no-go until rotation and dependent-job recovery are demonstrated.

## Error Handling

| Failure | Response |
| --- | --- |
| Required evidence is missing | Return no-go and name the owner and exact proof required. |
| Provider limit has no headroom | Reduce workload or obtain approved capacity before launch. |
| Rollback is untested | Rehearse it in non-production and retain the receipt before approval. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Clari Revenue API reference](https://developer.clari.com/default/documentation/external_spec)
- [Clari Copilot API reference](https://api-doc.copilot.clari.com/)
- [Clari service status](https://clari.statuspage.io/)
