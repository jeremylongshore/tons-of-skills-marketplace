---
name: salesforce-prod-checklist
description: 'Gate a Salesforce integration or metadata change for production with contract, security, capacity, validation, canary, reconciliation, and rollback evidence. Use when preparing for go-live. Trigger with "review Salesforce production readiness".'
argument-hint: "[release-id] [production-org]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, production, readiness, change-control]
model: inherit
effort: high
compatibility: Designed for Claude Code; production deployments and record changes require formal customer change approval
---
# Salesforce Production Readiness Gate

## Overview

Convert a release candidate into an evidence-backed go or no-go decision with named owners, bounded execution, and tested recovery.

## Prerequisites

- Immutable release candidate, change record, production org, maintenance window, and business owner
- Validated metadata and integration dependencies, API versions, permissions, limits, data mappings, and test evidence
- Canary, reconciliation, rollback or compensating action, communications, and Salesforce Support plans

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce release behavior depends on org metadata, automation, permissions, seasonal version, API support, entitlements, and shared capacity. Validation in a lower org reduces risk but does not prove production parity.

## Authentication

Use separate named non-production and production authorization with minimum deployment and verification permissions. Production credentials must be protected, short-lived where supported, auditable, and unavailable to fork-origin code.

## Instructions

1. Freeze the candidate SHA, metadata manifest, adapter artifact, dependency lock, API contract, and generated outputs.
2. Compare production and validation orgs for edition, features, packages, schema, permissions, sharing, automation, limits, and data assumptions.
3. Review security, privacy, segregation-of-duties, destructive-change, backfill, event, and support impacts.
4. Run static checks, unit tests, Apex or Flow tests, deployment validation, contract tests, and synthetic integration checks.
5. Approve a small canary with explicit users, objects, records, time box, stop signals, and rollback owner.
6. Execute only in the window, preserve deployment and request IDs, and monitor platform, application, limit, event, and business signals.
7. Reconcile metadata and data invariants, decide promote or rollback, communicate outcome, and retain the evidence bundle.

## Approval Boundaries

Do not approve, deploy, activate, mutate, backfill, or disable controls without release, Salesforce admin, security, data, and business-owner authorization.

## Output

Return a signed readiness matrix, parity gaps, gate results, canary scope, stop signals, deployment receipt, reconciliation, rollback state, and follow-up owners.

## Error Handling

| Condition | Response |
|---|---|
| Production parity gap is unresolved | Issue a no-go and assign the gap; do not waive it through a checklist edit. |
| Canary breaches a stop signal | Pause or rollback according to the approved plan before further rollout. |
| Rollback cannot restore the invariant | Use the documented compensating action and escalate severity. |

## Example

A redacted completion receipt might look like this:

```text
release=SF-1.8; candidate=immutable; gates=pass; canary=approved; deployed=yes; reconciled=yes; rollback=ready
```

## Resources

- [Salesforce DX development model](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_develop.htm)
- [Salesforce release notes](https://help.salesforce.com/s/articleView?id=release-notes.salesforce_release_notes.htm)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
