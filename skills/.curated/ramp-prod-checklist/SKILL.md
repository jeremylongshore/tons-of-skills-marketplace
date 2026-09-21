---
name: ramp-prod-checklist
description: >-
  Run a fail-closed readiness review for a Ramp integration before enabling production traffic or financial writes. Use when launching, expanding scopes, or changing architecture materially. Trigger with "Ramp production checklist" or "launch Ramp integration".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, production, readiness, governance]
---
# Ramp Production Readiness Gate

## Overview

Convert launch assumptions into evidenced gates. Review the exact artifact, environment, OAuth authority, data handling, endpoint contracts, reconciliation, incident controls, and rollback before any production write.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Production is isolated from sandbox and requires its own Ramp application, credentials, scopes, redirects, subscriptions, and approved business access.
- Third-party integrations use Authorization Code; internal server integrations may use Client Credentials.
- Card, accounting, bill, reimbursement, and other writes create business effects that need endpoint-specific idempotency and reconciliation.
- Current OpenAPI and guide exports may supersede copied examples or generated client assumptions.

## Instructions

1. Freeze the exact artifact, dependency lock, configuration digest, schema checksum, target entities, operations, scopes, event types, data classes, and owners.

2. Prove production host/application/secret provenance, minimum authority, credential rotation, negative access, and no sandbox fallback.

3. Pass unit, contract, schema-drift, security, redaction, pagination, retry, idempotency, duplicate-event, deferred-task, and rollback tests.

4. Execute a read-only production inventory and reconcile expected entities and source objects; resolve every unexplained difference.

5. Obtain independent approvals, canary the smallest cohort with writes explicitly enabled, reconcile business effects, and record go/no-go plus rollback authority.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

Application, security, privacy, business, and finance/accounting owners approve their boundaries. One operator may not self-approve all production risk.

## Output

A signed readiness matrix tied to an exact artifact/config, authority and data inventories, test evidence, read-only baseline, canary reconciliation, rollback plan, and launch decision.

## Error Handling

| Condition | Response |
|---|---|
| A required gate has no owner | Block launch and assign accountable ownership; absence is not a waiver. |
| The final artifact differs from tested bytes | Retest the exact candidate and invalidate prior approval. |
| Canary has an unexplained mismatch | Disable writes and resolve it before expanding traffic. |

## Examples

### Example 1

Launch a read-only analytics connector after scope denial tests, data review, and one-entity production reconciliation.

### Example 2

Enable accounting writes for a five-object cohort only after ERP and Ramp receipts match exactly.

## Validation

- Approvals reference the exact immutable artifact and configuration.
- Scopes, entities, subscriptions, data flows, and writes match the reviewed inventory.
- All tests and negative-access checks pass on current contracts.
- Canary, reconciliation, stop conditions, and rollback are complete before expansion.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
