---
name: clari-hello-world
description: >-
  Run one bounded Clari forecast export through request, status polling, and result retrieval. Use when proving Revenue API connectivity or learning the job lifecycle. Trigger with: "run my first Clari export", "test Clari connectivity", "export a forecast snapshot".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[forecast-id-time-period-and-output-format]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - clari
  - forecast
  - export
  - quickstart
compatibility: 'Requires a Revenue API token, access to an existing Forecast Tab, and permission to export its hierarchy.'
---

# First Clari Forecast Export

## Overview

Prove the complete asynchronous export contract with one small, non-production forecast request. Success means retaining the forecast ID, job ID, terminal state, result format, and a redacted schema sample—not merely receiving an initial HTTP response.

## Prerequisites

- Forecast Tab ID copied from the entitled Clari Forecast view
- A scoped Revenue API token stored outside the repository
- A small time period, hierarchy scope, and approved output location

## Instructions

### Step 1: Freeze the request

Record the forecast ID, time period, requested data types, scope ID, currency, history choice, and JSON or CSV format.

### Step 2: Check capacity

Read `/admin/limits` and confirm both concurrent capacity and rolling monthly quota before consuming an export slot.

### Step 3: Queue the export

Submit `POST /export/forecast/{forecastId}` against the documented Revenue API base and retain the returned job ID.

### Step 4: Poll deliberately

Read `/export/jobs/{jobId}` with bounded backoff until `DONE`, `ABORTED`, or an operator-defined timeout. Do not treat `SCHEDULED` or `STARTED` as completion.

### Step 5: Retrieve once

Only after `DONE`, fetch `/export/jobs/{jobId}/results`, validate content type and shape, and store the result in the approved temporary boundary.

### Step 6: Close the proof

Record row count, schema fingerprint, status timeline, and cleanup result; delete temporary exported data according to policy.

## Authentication

Use the Revenue API token only in the `apikey` header over HTTPS. Never include the header, raw response body, or revenue values in logs; authorization follows the token owner’s Clari access and hierarchy.

## Tool Discipline

Use Read and Grep to inspect configuration, provider contracts, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not issue, rotate, revoke, create, update, cancel, delete, export, ingest, or publish provider data without explicit operator approval.

## Output

- Redacted request manifest and returned job ID
- Terminal-state timeline and result schema fingerprint
- Pass/fail decision with cleanup receipt

Return the exact surface, environment, resource or job identifiers, contract fingerprint, evidence, unresolved risks, and final decision without exposing credentials or sensitive customer data.

## Examples

An operator requests a JSON export for one current-quarter Forecast Tab, observes `SCHEDULED`, `STARTED`, and `DONE`, retrieves the result once, and records field names and row count without retaining deal values in the test artifact.

## Error Handling

| Failure | Response |
| --- | --- |
| Forecast ID rejected | Re-copy the ID from the intended Forecast Tab and verify the integration identity is opted into that hierarchy. |
| Job remains non-terminal | Stop at the timeout, retain the job ID, inspect service status, and avoid queuing duplicate jobs. |
| Results request fails | Confirm the job is `DONE`, the job ID belongs to the same token, and the export has not expired. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Clari Revenue API reference](https://developer.clari.com/default/documentation/external_spec)
- [Clari service status](https://clari.statuspage.io/)
