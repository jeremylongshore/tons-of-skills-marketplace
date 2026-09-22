---
name: workhuman-upgrade-migration
description: 'Migrate a Workhuman API, managed connector, schema, identity, or program configuration under contract and reconciliation controls. Use when managing upgrades and breaking changes. Trigger with "plan a Workhuman migration".'
argument-hint: "[current-contract] [target-contract]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.4.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, workhuman, migration, upgrade, change-management]
model: inherit
effort: high
compatibility: Designed for Claude Code; tenant, identity, worker, award, financial, and connector changes require accountable owner approval
---
# Workhuman Contract and Integration Migration

## Overview

Move from a frozen current state to a frozen target while preserving worker authority, recognition history, award integrity, and a tested rollback path.

## Prerequisites

- Current and target customer-authorized contracts, schemas, mappings, entitlements, and configurations
- Complete consumer, producer, principal, schedule, and data-flow inventory
- Business, HCM, payroll, identity, security, privacy, integration, and support owners

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect dependencies and artifacts, `WebFetch` for current vendor context, and `Write` or `Edit` for mappings, compatibility code, fixtures, plans, and redacted receipts.

## Current Contract

Workhuman's public capability pages do not define one universal versioning or deprecation policy for customer APIs and managed integrations. The customer's notices, implementation artifacts, and support guidance control the migration.

## Authentication

Map current and target principals, privileges, environments, rotation, revocation, and overlap. Do not keep legacy access active indefinitely or broaden permissions to simplify migration.

## Instructions

1. Freeze source and target artifacts by version or digest and record retrieval date, tenant, owner, and effective window.
2. Inventory changed operations, fields, meanings, identities, schedules, limits, integration behavior, and subscribed capabilities.
3. Build a field-level compatibility matrix covering authority, defaults, nullability, identifiers, effective dates, currencies, and deletion semantics.
4. Classify consumers as compatible, adapter-required, dual-read, dual-write, backfill, or retire; prove each classification with fixtures.
5. Test valid, empty, duplicate, late, partial, rejected, revoked-auth, drift, rollback, and reconciliation scenarios.
6. Present canary population, financial exposure, communications, cutover, abort thresholds, overlap duration, and rollback.
7. After approval, canary the target and compare both authoritative state and downstream effects before expansion.
8. Revoke obsolete access, remove compatibility code on schedule, and preserve a redacted migration receipt.

## Approval Boundaries

Do not change tenant configuration, mappings, principals, schedules, worker data, awards, or production traffic without all affected owners.

## Output

Return source and target identities, change and compatibility matrices, test evidence, canary plan, approvals, reconciliation, rollback state, and decommission schedule.

## Error Handling

| Condition | Response |
|---|---|
| Target meaning is ambiguous | Stop and obtain a vendor ruling; do not map by field name alone. |
| Canary diverges | Halt expansion, preserve checkpoints, and execute the approved rollback. |
| Legacy principal remains necessary | Record an owner and expiry rather than leaving permanent overlap. |

## Example

A redacted completion receipt might look like this:

```text
source=contract@old-digest; target=contract@new-digest; consumers=6; canary=20; divergence=0; legacy-revoke=scheduled
```

## Resources

- [Workhuman integrations](https://www.workhuman.com/capabilities/integrations/)
- [Workhuman security and privacy](https://www.workhuman.com/why-workhuman/security-and-privacy/)

## Next Steps

Track decommissioning until obsolete credentials, mappings, fixtures, schedules, and compatibility code are removed.
