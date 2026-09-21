---
name: procore-cost-tuning
description: >-
  Recover Procore API capacity by eliminating failed calls, redundant polling, repeated lookups, and unused payloads. Use when request volume, infrastructure spend, or backlog growth is high; this workflow does not invent provider pricing. Trigger with: "reduce Procore API calls", "cut Procore sync cost", "stop Procore polling".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[workload-and-cost-signal]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - efficiency
  - api-budget
compatibility: 'Requires the Procore API Call Activity Report or equivalent route-level request counts plus infrastructure cost telemetry.'
---

# Procore API Call Budget Recovery

## Overview

Treat calls, worker time, transfer, and backlog as measured costs. Procore documents request limits and activity reporting, but not a universal per-call price, so financial claims must come from the operator's own infrastructure and agreement.

## Prerequisites

- Route, method, status, and daily count from the API Call Activity Report
- Poll interval, worker utilization, transfer, storage, and queue metrics
- Freshness objective and correctness oracle for every optimized resource

## Instructions

### Step 1: Build the denominator

Rank normalized routes by total calls, failed calls, payload volume, and worker time. Separate unavoidable business traffic from retries, polling, and adapter defects.

### Step 2: Eliminate failed-call waste

Fix recurring 400, 403, and 404 traffic first because unsuccessful requests consume rate budget. Remove private or deprecated routes rather than retrying them.

### Step 3: Replace polling carefully

Use webhooks for prompt change notification and retain a lower-frequency reconciliation sync for completeness. Do not claim webhooks are a guaranteed event log.

### Step 4: Collapse repeat reads

Cache stable company and project metadata, request collections instead of per-record reads, and use only documented filters, pagination, or sync actions.

### Step 5: Quantify savings

Compare calls per useful changed record, failed-call share, compute time, transfer, backlog age, and infrastructure cost. Keep provider fees separate unless an authoritative contract supplies them.

### Step 6: Guard freshness

Run a full reconciliation and compare state hashes. Roll back any optimization that misses records, delays required updates, or expands permissions.

## Authentication

Optimized requests continue using the existing OAuth 2.0 Bearer token and company scope. Credential multiplication is not a cost or rate-control strategy and must never be used to bypass limits.

## Tool Discipline

Use Read and Grep to inspect activity reports, metrics, call sites, and endpoint contracts. Use Write or Edit only for the approved optimization, test, budget, or receipt; do not modify Procore data during cost analysis.

## Output

- Route-level waste and cost denominator
- Approved optimizations with correctness evidence
- Before-and-after API, infrastructure, freshness, and rollback metrics

Return measured savings and explicitly label any cost component that is unknown.

## Examples

An hourly poll mostly returns unchanged RFIs while 404 retries consume capacity. The integration fixes the access defect, uses webhook notifications for prompt reads, and retains a nightly reconciliation that proves no records were missed.

## Error Handling

| Failure | Response |
| --- | --- |
| Provider price is unknown | Report request and infrastructure measurements without inventing a monetary rate. |
| Webhook gaps appear | Increase reconciliation coverage and repair delivery handling. |
| Cache serves stale authorization data | Shorten or invalidate the cache; access correctness outranks savings. |
| Fewer calls miss records | Roll back and restore the last complete synchronization strategy. |

## Resources

- [First-party source notes](references/official-docs.md)
- [API Call Activity Report](https://developers.procore.com/documentation/api-activity-export)
- [Rate limiting](https://developers.procore.com/documentation/rate-limiting)
- [Webhook reliability](https://developers.procore.com/documentation/webhooks)
