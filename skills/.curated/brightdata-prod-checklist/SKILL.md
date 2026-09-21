---
name: brightdata-prod-checklist
description: 'Gate a Bright Data integration for production with authorization, reliability, cost, data, and rollback evidence. Use when promoting a proxy, Browser API, scraper, snapshot, or delivery workload. Trigger with: "production checklist for Bright Data", "approve this Bright Data rollout", "review a Bright Data release".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: "[release-candidate]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- web-data
- bright-data
- prod-checklist
- operations
compatibility: 'Requires an approved Bright Data account or offline fixtures, current Bright Data documentation, and an authorized public-data collection purpose'
---
# Bright Data Production Readiness Gate

## Overview

Make production promotion a fail-closed evidence decision. A green connectivity test is insufficient without target authorization, schema and data controls, secret ownership, backpressure, observability, and a tested rollback.

## Prerequisites

- A release candidate tied to an approved workload manifest
- Staging results for success and documented failure classes
- Named service, data, security, finance, and rollback owners

## Instructions

### Step 1: Validate authority

Read approvals and Grep runtime configuration for unlisted targets, fields, products, zones, or delivery destinations. Verify public-data scope and recipient and retention decisions.

### Step 2: Validate controls

Confirm secret-manager binding, environment isolation, egress allowlists, redirect denial, byte, record, and job ceilings, adaptive backpressure, redacted telemetry, and idempotent processing.

### Step 3: Exercise failure paths

Write or Edit tests for revoked credentials, policy 403, 429, provider 5xx, snapshot failure or expiry, malformed schema, oversized delivery, duplicate delivery, and downstream outage.

### Step 4: Canary and decide

Run a bounded approved canary through the deployment workflow. Compare authorization, success, error, latency, cost, and data-quality thresholds; promote only with a rollback receipt.

## Tool Discipline

Use Read and Grep for release-evidence inspection. Use Write and Edit for missing tests, manifests, runbooks, and the decision record. This skill does not change production credentials, zones, traffic, or delivery destinations.

## Output

- Pass or fail matrix for authority, safety, reliability, cost, and data
- Canary metrics and explicit promotion decision
- Rollback trigger, procedure, owner, and proof

## Examples

Release one worker with a low job and byte ceiling and an approved test target. Promote only after duplicate delivery, policy denial, secret redaction, schema quarantine, and rollback drills all produce their expected receipts.

## Error Handling

| Failure | Meaning | Response |
|---------|---------|----------|
| A required owner has not approved | Release authority is incomplete | Keep the candidate staged |
| Rollback depends on an untested old zone | Recovery is speculative | Run the rollback drill before promotion |
| Canary produces unexpected fields | Data contract drifted | Quarantine results and fail the gate |

## Resources

- [Acceptable use policy](https://docs.brightdata.com/general/policy/acceptable-use-policy)
- [Proxy error catalog](https://docs.brightdata.com/proxy-networks/errorCatalog)
- [Network status](https://brightdata.com/network-status)
- [Scraper data delivery](https://docs.brightdata.com/products/scrapers/scrapers-library/data-delivery)
