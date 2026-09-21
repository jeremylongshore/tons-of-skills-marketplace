---
name: salesforce-core-workflow-b
description: 'Analyze and run the correct Salesforce high-volume operation using Bulk API 2.0, Composite, Graph, or sObject Collections with reconciliation. Use when handling large or dependent batches. Trigger with "run a Salesforce bulk workflow".'
argument-hint: "[org-alias] [dataset] [operation]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, bulk-api, composite-api, reconciliation]
model: inherit
effort: high
compatibility: Designed for Claude Code; high-volume writes require capacity, data-owner, automation-owner, and production change approval
---
# Salesforce High-Volume and Composite Operation

## Overview

Choose an API from workload evidence, make every batch restartable, and prove final state across partial, asynchronous, and dependent outcomes.

## Prerequisites

- Dataset classification, object dependencies, operation, expected counts, external IDs, and owners
- Current Bulk API 2.0, Composite, Graph, and sObject Collections documentation
- Org limits, automation cost, error budget, maintenance window, quarantine, and rollback plans

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Bulk API 2.0 performs asynchronous CSV ingest and large queries. Composite APIs combine supported REST subrequests with documented dependency and limit semantics; the best choice depends on volume, dependency graph, latency, and atomicity needs.

## Authentication

Use a dedicated approved principal with only the required API, object, and field permissions. Keep tokens and payload data out of logs, plans, fixtures, and support bundles.

## Instructions

1. Profile row count, payload size, dependencies, ordering, latency, atomicity, retry, and reconciliation requirements.
2. Inspect org entitlements, current API versions, limits, object metadata, automation, external IDs, and lock risks.
3. Select Bulk API 2.0 for suitable asynchronous volume or the documented Composite resource for bounded dependent requests.
4. Normalize and validate data, split deterministic batches, assign stable source keys, and create a quarantine ledger.
5. Run a synthetic or read-only proof, then a small approved non-production write canary.
6. Execute within the approved capacity window while recording job, graph, batch, request, and result identifiers.
7. Download successes and failures, re-query target state, reconcile counts and keys, and retry only classified safe subsets.

## Approval Boundaries

Do not start high-volume jobs, select serial or parallel behavior, bypass automation, or retry uncertain writes without data, platform, and change-owner approval.

## Output

Return the API decision, capacity plan, batch manifest, job identifiers, success and failure ledgers, reconciliation evidence, and rollback or resume point.

## Error Handling

| Condition | Response |
|---|---|
| Job completes with failed records | Quarantine exact failures and preserve source keys; never replay the whole dataset blindly. |
| Dependent composite request fails | Use documented response status and dependency semantics to determine what committed before compensation. |
| Locks or automation exceed the stop threshold | Pause intake, preserve job state, and revise ordering, concurrency, or window with owners. |

## Example

A redacted completion receipt might look like this:

```text
mode=bulk-v2-upsert; rows=120000; key=Legacy_Id__c; canary=100-pass; success=119980; quarantine=20; reconciled=yes
```

## Resources

- [Bulk API 2.0](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/bulk_api_2_0.htm)
- [Composite REST resources](https://developer.salesforce.com/docs/platform/api-rest/guide/resources-composite-composite.html)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
