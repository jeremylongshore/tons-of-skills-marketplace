---
name: clari-reference-architecture
description: >-
  Design a Clari architecture that separates Revenue exports, v2 ingestion, Copilot, control state, landing, validation, and publication. Use when defining or reviewing a platform boundary. Trigger with: "design Clari architecture", "review a Clari topology", "map Clari data flow".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[surfaces-destinations-and-recovery-objectives]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - clari
  - architecture
  - governance
  - reliability
compatibility: 'Requires approved Clari products, destination systems, data classifications, service objectives, and platform ownership.'
---

# Clari Governed Integration Architecture

## Overview

Separate control-plane state from sensitive data and isolate each provider surface behind its own adapter. The architecture should make job identity, cursor state, source lineage, schema versions, mutations, and published datasets independently auditable.

## Prerequisites

- Business flows and read/write endpoint inventory
- Data-classification, retention, residency, and access requirements
- Recovery point, recovery time, freshness, and reconciliation objectives

## Instructions

### Step 1: Draw trust boundaries

Place Revenue, ingestion, Copilot, secrets, scheduler, state store, landing zone, validator, warehouse, and consumers in explicit zones.

### Step 2: Separate provider adapters

Use distinct hosts, credential types, schemas, limiters, and mutation policies for each surface.

### Step 3: Design durable control state

Persist request fingerprints, provider job IDs, cursors, terminal states, contract fingerprints, and retry decisions outside ephemeral workers.

### Step 4: Design the data path

Land immutable results, validate and reconcile in quarantine, normalize with lineage, then atomically publish approved versions.

### Step 5: Design failure containment

Prevent provider failure, schema drift, partial load, or unauthorized mutation from advancing consumer-facing data.

### Step 6: Prove operability

Walk happy path, provider outage, quota exhaustion, credential rotation, schema drift, rollback, deletion, and support escalation.

## Authentication

Keep credential issuance and rotation in a dedicated secrets boundary. Adapters receive references for only one surface and environment, while downstream processors receive data but no provider credentials.

## Tool Discipline

Use Read and Grep to inspect configuration, provider contracts, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not issue, rotate, revoke, create, update, cancel, delete, export, ingest, or publish provider data without explicit operator approval.

## Output

- Trust-boundary and data-flow diagram
- Component ownership and contract matrix
- Failure, recovery, rollback, retention, and deletion walkthrough

Return the exact surface, environment, resource or job identifiers, contract fingerprint, evidence, unresolved risks, and final decision without exposing credentials or sensitive customer data.

## Examples

The Revenue adapter writes job state to a control store and results to restricted landing storage; a validator publishes normalized snapshots. Copilot uses a different adapter and sensitive-data zone, while ingestion is isolated behind an approval-gated writer.

## Error Handling

| Failure | Response |
| --- | --- |
| One component holds every credential | Split adapters and least-privilege identities before production approval. |
| Raw landing writes directly to dashboards | Insert validation, reconciliation, versioning, and atomic publication. |
| Mutation and read paths share retries | Separate policies so a transient read retry cannot replay a write. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Clari Revenue API reference](https://developer.clari.com/default/documentation/external_spec)
- [Clari Copilot API reference](https://api-doc.copilot.clari.com/)
