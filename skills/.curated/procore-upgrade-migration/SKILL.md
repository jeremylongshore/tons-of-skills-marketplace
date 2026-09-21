---
name: procore-upgrade-migration
description: >-
  Migrate one Procore endpoint contract after a lifecycle, deprecation, version, or webhook payload change using observed traffic and dual-read evidence. Use when the changelog announces a replacement or Integration Health detects deprecated usage. Trigger with: "upgrade a Procore API version", "remove deprecated Procore endpoint", "migrate Procore webhook payload".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[old-contract-and-replacement-contract]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - api-lifecycle
  - migration
compatibility: 'Requires current Procore API reference and changelog access plus route-level production traffic evidence.'
---

# Procore Endpoint Contract Cutover

## Overview

Migrate the concrete resource and operation named by provider evidence. Procore does not expose one universal pack-wide version transition, so never claim a generic v1-to-v1.1 upgrade without endpoint-specific documentation.

## Prerequisites

- Deprecated route, method, version, or payload format and documented replacement
- API Call Activity Report slice covering every deployed caller
- Old and new response contracts, test fixtures, rollout owner, and removal deadline

## Instructions

### Step 1: Prove affected traffic

Find the normalized deprecated route in production activity and search every service, scheduled job, event handler, and shared adapter for callers.

### Step 2: Diff contracts

Compare paths, headers, IDs, query parameters, request fields, response fields, pagination, permissions, status codes, webhook schema, and lifecycle phase.

### Step 3: Build a compatibility adapter

Isolate the new contract behind a resource-specific interface. Normalize only fields the business layer truly needs and preserve provider errors and metadata.

### Step 4: Verify side by side

For reads, compare sanitized result sets and state hashes. For writes, use sandbox fixtures or a provider-supported idempotent strategy; do not duplicate live mutations.

### Step 5: Roll out by cohort

Canary the new adapter, monitor error and rate signals, and keep an explicit rollback boundary while the old route remains supported.

### Step 6: Remove the old path

After traffic evidence reaches zero and the observation clears, remove compatibility code, fixtures, configuration, and documentation for the deprecated contract.

## Authentication

Both contracts use the intended OAuth 2.0 principal and company boundary. A migration must not widen DMSA permissions or switch grant types unless that separate security change is reviewed.

## Tool Discipline

Use Read and Grep to inspect changelogs, activity reports, adapters, and callers. Use Write or Edit only for the approved adapter, migration test, rollout configuration, or receipt; do not perform duplicate live writes.

## Output

- Provider evidence and complete caller inventory
- Contract diff, compatibility adapter, and equivalence tests
- Canary, rollback, zero-traffic, and removal receipt

Return the exact old and new contracts, affected volume, semantic differences, rollout status, and deletion evidence.

## Examples

A deprecated webhook route is still called by one monthly job. The team adds the documented scoped replacement, verifies payload and permission differences, canaries it, and removes the legacy route only after the API activity report shows no callers.

## Error Handling

| Failure | Response |
| --- | --- |
| Replacement is not documented | Stop and contact Procore API support rather than guessing a private route. |
| Read results diverge | Classify each delta and delay cutover until expected differences are approved. |
| New contract needs more permission | Review the manifest change separately and rerun negative-access tests. |
| Old traffic persists | Find the remaining caller; do not delete compatibility code. |

## Resources

- [First-party source notes](references/official-docs.md)
- [API lifecycle](https://developers.procore.com/documentation/rest-api-lifecycle)
- [API changelog](https://developers.procore.com/documentation/changelog)
- [Integration Health](https://developers.procore.com/documentation/integration-health)
