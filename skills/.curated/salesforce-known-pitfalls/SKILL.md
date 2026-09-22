---
name: salesforce-known-pitfalls
description: 'Review a Salesforce integration for fixed API versions, unsafe auth, N-plus-one queries, shared-limit blindness, stale metadata, blind retries, event gaps, and missing reconciliation. Use when preparing a release. Trigger with "audit Salesforce pitfalls".'
argument-hint: "[repository] [integration]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, pitfalls, review, prevention]
model: inherit
effort: high
compatibility: Designed for Claude Code; remediation that changes access, queries, workloads, events, or records requires the corresponding owner approval
---
# Salesforce Integration Pitfall Audit

## Overview

Find evidence of recurring failure patterns in code and operations, rank their real blast radius, and convert each confirmed issue into a bounded fix and regression test.

## Prerequisites

- Repository, architecture, org topology, API and event contracts, deployment history, incidents, and current owners
- Current Salesforce API EOL, OAuth, limits, metadata, security, Bulk, Composite, CDC or Pub/Sub documentation
- Representative fixtures, non-production org, policy gates, reconciliation queries, and change process

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Common Salesforce defects cross application and org boundaries: unsupported versions, legacy auth, inefficient queries, shared capacity, object or field drift, automation side effects, partial writes, event gaps, and permission differences. Their exact behavior must be proven in context.

## Authentication

Audit secret references and authorization boundaries without resolving live secrets. Use the real integration principal only in a protected authorized test lane, never an administrator session as proof.

## Instructions

1. Inventory hard-coded API versions, login hosts, app types, OAuth flows, secrets, org aliases, direct calls, queries, writes, retries, and event state.
2. Detect N-plus-one and unbounded queries, broad field selection, missing pagination, stale metadata, wrong API mode, and unmeasured automation.
3. Check shared limits, concurrency, hard-quota behavior, timeout classification, partial results, uncertain-write reconciliation, and batch idempotency.
4. Review CRUD and field access, sharing, SOQL construction, logs, exports, support bundles, production data in fixtures, and privileged bypasses.
5. Inspect event schemas, checkpoints, duplicates, ordering, gap and overflow handling, dead letters, reconciliation, and backfill.
6. Rank confirmed findings by exploitability, data and business impact, likelihood, detectability, and recovery cost.
7. Remediate one boundary at a time with negative fixtures, protected canaries, rollback, and invariant reconciliation.

## Approval Boundaries

Do not resolve findings by broadening permissions, disabling automation, increasing retries, raising concurrency, resetting checkpoints, or deleting data without owners.

## Output

Return the pitfall inventory, evidence and severity, false positives, prioritized fixes, tests, canary and rollback plans, reconciliation, and owners.

## Error Handling

| Condition | Response |
|---|---|
| Finding depends on an unverified org assumption | Label it provisional and collect the minimum protected evidence. |
| Suggested fix moves risk to another integration | Reassess shared limits, authority, data, event, and recovery effects across the architecture. |
| Legacy behavior has no owner | Escalate ownership before mutation and add monitoring in the interim. |

## Example

A redacted completion receipt might look like this:

```text
integration=lead-sync; findings=9; critical=1-fixed; high=3-owned; fixtures=12; canary=pass; reconcile=exact
```

## Resources

- [REST API end-of-life policy](https://developer.salesforce.com/docs/platform/api-rest/guide/api-rest-eol.html)
- [REST API limits](https://developer.salesforce.com/docs/platform/api-rest/guide/resources-limits.html)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
