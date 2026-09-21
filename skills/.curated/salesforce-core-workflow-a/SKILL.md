---
name: salesforce-core-workflow-a
description: 'Run a metadata-aware Salesforce record workflow with bounded SOQL, CRUD and field-access checks, mutation preview, and reconciliation. Use when operating transactional objects. Trigger with "operate Salesforce records".'
argument-hint: "[org-alias] [object] [operation]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, soql, records, metadata]
model: inherit
effort: high
compatibility: Designed for Claude Code; record mutations require business object owner approval and a tested rollback or compensating action
---
# Governed Salesforce Record and SOQL Workflow

## Overview

Turn a record request into a permission-aware, selective, idempotent, and auditable operation instead of embedding fixed object assumptions.

## Prerequisites

- Authorized org, object, business purpose, selection rule, and data owner
- Current object metadata, CRUD and field access, sharing context, automation, and duplicate rules
- Expected counts, external keys, mutation policy, rollback method, and reconciliation owner

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

REST and SOQL operations are versioned and execute in the security context of the authorized principal. Object metadata, fields, validation, triggers, flows, sharing, and duplicate behavior vary by org.

## Authentication

Use the approved integration principal and OAuth contract. Prove object and field access for that principal; do not infer authorization from an administrator session or from metadata visible to another user.

## Instructions

1. Record the business invariant, org, object, fields, predicates, expected count, external key, and accountable owner.
2. Discover a supported API version and inspect current object and field metadata for the principal.
3. Build a selective parameterized query with explicit fields, scope, ordering, row bound, and pagination plan.
4. Run a read-only sample and compare counts, ownership, duplicates, nullability, and sensitive-data classification.
5. Preview create, update, upsert, or delete effects including validation, automation, sharing, and downstream integrations.
6. After explicit approval, execute a bounded idempotent batch and retain request and result identifiers without record data.
7. Re-query by stable key, reconcile success and failure counts, quarantine exceptions, and invoke rollback if invariants fail.

## Approval Boundaries

Do not mutate records, bypass validation, use broad queries, change sharing, or expose field values without object, data, and change-owner approval.

## Output

Return the query and metadata evidence, expected and actual counts, permission findings, mutation preview, request IDs, exceptions, reconciliation, and rollback status.

## Error Handling

| Condition | Response |
|---|---|
| Metadata changed after planning | Stop and rebuild the query and mutation preview from the new contract. |
| Partial mutation failure occurs | Do not blind-retry; classify records, preserve idempotency, and quarantine uncertain outcomes. |
| Query is non-selective or unbounded | Add supported predicates and bounds or choose an asynchronous pattern. |

## Example

A redacted completion receipt might look like this:

```text
org=uat; object=Account; query=bounded; expected=25; approved=25; succeeded=24; quarantined=1; reconciled=yes
```

## Resources

- [Execute a SOQL query](https://developer.salesforce.com/docs/platform/api-rest/guide/dome-query.html)
- [Work with object metadata](https://developer.salesforce.com/docs/platform/api-rest/guide/using-resources-working-with-object-metadata.html)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
