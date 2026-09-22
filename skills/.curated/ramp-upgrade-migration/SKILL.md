---
name: ramp-upgrade-migration
description: >-
  Upgrade a Ramp integration across API, schema, scope, endpoint, or behavior changes using impact analysis, dual verification, and reversible rollout. Use when addressing changelog items, deprecated endpoints, or regenerated clients. Trigger with "upgrade Ramp API" or "Ramp breaking change".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, upgrade, schema-drift, deprecation]
---
# Ramp API Contract Upgrade

## Overview

Treat documentation or schema drift as a migration. Diff the exact contracts, map affected business behavior and stored data, then canary a reviewed artifact without silently changing scopes or writes.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Ramp publishes a changelog, OpenAPI schema, guide exports, and API reference; each may reveal a different class of impact.
- Legacy Cards endpoints are being deprecated for virtual-card management in favor of Funds and Cards (Virtual).
- Adding configured scopes does not update an existing token; new tokens are required.
- Unknown fields may be accepted or rejected by endpoint, so compatibility must be tested against the current schema.

## Authentication

Preserve the approved OAuth grant and minimum scopes while comparing contracts. If required scopes change, configure them through review, issue a new environment-bound bearer token, revoke superseded credentials, and repeat positive and negative authority tests.

## Instructions

1. Freeze old and new OpenAPI checksums, relevant guide/changelog snapshots, client version, endpoint manifest, scopes, stored schemas, and exact deployed artifact.

2. Diff paths, verbs, request/response fields, enums, requiredness, pagination, money units, errors, limits, deprecations, and authorization.

3. Classify each consumer and stored record as compatible, adapter-needed, backfill-needed, behavior-changed, scope-changed, or blocked.

4. Update a narrow adapter and fixtures, issue new minimum-scope tokens if required, and run old/new sandbox tests plus rollback compatibility.

5. Deploy dark, canary one bounded cohort, reconcile results and business effects, then expand or roll back with preserved checkpoints.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

API/application owners approve contract changes; security approves new grants/scopes; data/finance owners approve schema, backfill, and business-effect changes.

## Output

A contract diff, impact matrix, migration/backfill plan, token and scope plan, deterministic and sandbox evidence, canary reconciliation, and rollback record.

## Error Handling

| Condition | Response |
|---|---|
| A regenerated client changes unrelated endpoints | Restrict generation/export surface and review only the required contract delta. |
| New scope works in config but requests still fail | Acquire a new token and verify its bound scopes and environment. |
| Rollback cannot read newly written data | Keep writes disabled until dual-read or reversible migration is proven. |

## Examples

### Example 1

Move virtual-card management off deprecated legacy Cards operations to fund-backed current endpoints with sandbox lifecycle proof.

### Example 2

Adopt a changed accounting response field while dual-reading old stored records and reconciling one entity.

## Validation

- Every changed contract element maps to code, test, data, authority, or an explicit no-impact decision.
- The exact new artifact passes current-schema and rollback tests.
- Scope changes use newly issued tokens and repeat negative tests.
- Canary records reconcile before wider traffic.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
