---
name: mindtickle-upgrade-migration
description: 'Migrate a Mindtickle tenant contract, adapter, connector, identity mapping, or product configuration through compatibility and rollback gates. Use when a vendor or customer contract changes. Trigger with "migrate Mindtickle integration".'
argument-hint: "[change-record] [target-version]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, mindtickle, migration, compatibility, rollback]
model: inherit
effort: high
compatibility: Designed for Claude Code; tenant, identity, data, connector, and production migrations require named customer and vendor approvals
---
# Controlled Mindtickle Contract Migration

## Overview

Move from a frozen current contract to a verified target while preserving identity, data meaning, operational continuity, and a tested reversal path.

## Prerequisites

- Current and target artifacts with provenance, digests, effective dates, and vendor or customer owners
- Inventory of affected operations, fields, identities, mappings, reports, programs, and downstream consumers
- Representative sanitized fixtures, a migration window, communications, and rollback authority

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect contracts, mappings, and consumers, `WebFetch` for current authorized change material, and `Write` or `Edit` for compatibility tests, migration plans, and redacted receipts.

## Current Contract

Mindtickle may update subscription services and tenant capabilities, while customer profile fields, integrations, custom reports, and migrations can require separately scoped work. Do not infer API versioning or backward compatibility when the authorized artifacts do not state it.

## Authentication

Validate target credential compatibility and scopes in non-production. Keep current and target credentials separately owned, prevent downgrade to broader access, and preserve revocation plans for both.

## Instructions

1. Freeze current and target contracts and build a semantic diff of operations, schemas, meanings, defaults, permissions, limits, and support status.
2. Trace every changed element to code, fixtures, identity mappings, reports, content, data stores, alerts, and business owners.
3. Classify changes as compatible, transformable, destructive, entitlement-dependent, or clarification required.
4. Define transformation, validation, duplicate prevention, reconciliation, retention, and rollback for each affected data set.
5. Run old fixtures against the new adapter and target fixtures against the compatibility boundary; include partial and ambiguous failures.
6. Rehearse migration and rollback with synthetic or approved non-production data and compare counts, identities, meanings, and permissions.
7. Present the exact change set, downtime or dual-run window, approvers, abort thresholds, and support coverage.
8. After approval, migrate incrementally, reconcile at each boundary, then revoke obsolete access only after the rollback window closes.

## Approval Boundaries

Do not transform learner records, change identity attributes, enable target writes, accept destructive loss, or revoke rollback credentials without accountable owners.

## Output

Return contract digests and diff, impact graph, migration and rollback plan, fixture results, rehearsal reconciliation, approvals, live receipts, and decommission decision.

## Error Handling

| Condition | Response |
|---|---|
| Meaning of a field changed ambiguously | Block that mapping and request authoritative clarification. |
| Rehearsal loses or duplicates records | Fail the gate and repair transformation or idempotency. |
| Live reconciliation crosses a threshold | Stop, preserve evidence, and execute the approved rollback. |

## Example

```text
current-contract=sha256:...; target=sha256:...; changes=4-compatible,1-blocked; rehearsal=exact; live=not-approved
```

## Resources

- [Mindtickle terms of service](https://www.mindtickle.com/legal/terms-of-service/)
- [Mindtickle professional services](https://www.mindtickle.com/legal/professional-services-scope-and-services-description/)

## Next Steps

Resolve blocked mappings, rerun the full rehearsal, and schedule obsolete-access revocation after acceptance.
