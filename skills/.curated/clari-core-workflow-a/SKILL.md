---
name: clari-core-workflow-a
description: >-
  Build a Clari forecast-export pipeline with reconciliation, schema controls, and warehouse lineage. Use when loading forecasts, quotas, adjustments, or CRM totals. Trigger with: "export Clari forecasts", "load Clari into the warehouse", "build a forecast pipeline".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[forecast-id-period-scope-and-warehouse]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - clari
  - forecast
  - warehouse
  - data-pipeline
compatibility: 'Requires Revenue API export entitlement, an existing Forecast Tab, an approved warehouse target, and governed handling of revenue data.'
---

# Clari Forecast Warehouse Pipeline

## Overview

Move forecast data through a three-stage pipeline: immutable landing, validated normalization, and reconciled publication. Preserve Clari identifiers and export context so every dashboard value can be traced back to one job and request.

## Prerequisites

- Forecast ID, hierarchy scope, fiscal-period convention, and requested data types
- Landing storage with encryption, retention, and access controls
- Warehouse schema owner and reconciliation tolerances

## Instructions

### Step 1: Define the snapshot key

Use forecast ID, requested time period, scope, currency, data types, and export timestamp as the immutable business key.

### Step 2: Reserve export capacity

Read organization limits and ensure the scheduler will not exceed concurrent or rolling quota constraints.

### Step 3: Run the asynchronous export

Queue the forecast job, poll boundedly to a terminal state, and retrieve the result only after `DONE`.

### Step 4: Land before transforming

Write the original approved result to immutable, access-controlled storage with job ID, content hash, contract fingerprint, and ingestion timestamp.

### Step 5: Normalize and reconcile

Map fields into versioned tables, preserve raw identifiers, check row counts and totals, and quarantine unknown fields or malformed monetary values.

### Step 6: Publish atomically

Expose the new snapshot only after reconciliation passes; otherwise keep the prior known-good snapshot and emit an actionable failure receipt.

## Authentication

Use a dedicated Revenue API integration identity and `apikey` header. Warehouse credentials must be separate from the Clari token, and logs must exclude both secrets and raw forecast values.

## Tool Discipline

Use Read and Grep to inspect configuration, provider contracts, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not issue, rotate, revoke, create, update, cancel, delete, export, ingest, or publish provider data without explicit operator approval.

## Output

- Immutable landing manifest tied to the Clari job ID
- Versioned normalized tables with lineage and schema checks
- Reconciliation report and atomic publish or rollback decision

Return the exact surface, environment, resource or job identifiers, contract fingerprint, evidence, unresolved risks, and final decision without exposing credentials or sensitive customer data.

## Examples

A quarterly forecast export lands as an immutable object, normalizes forecast and quota rows, reconciles counts and totals against the landing file, and advances the dashboard view only after all gates pass.

## Error Handling

| Failure | Response |
| --- | --- |
| Export is empty | Verify period, scope, data types, hierarchy access, and Forecast Tab configuration before publishing. |
| Schema adds an unknown field | Quarantine the snapshot, classify the field, and version the mapping before retrying publication. |
| Warehouse load partially succeeds | Rollback the staging transaction and retain the prior published snapshot. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Clari Revenue API reference](https://developer.clari.com/default/documentation/external_spec)
