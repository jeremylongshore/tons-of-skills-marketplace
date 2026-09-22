---
name: salesforce-migration-deep-dive
description: 'Run a dependency-ordered Salesforce data migration with mapping, external IDs, Bulk API selection, quarantine, cutover, reconciliation, and rollback. Use when conducting large migrations. Trigger with "migrate Salesforce data".'
argument-hint: "[source] [target-org] [dataset]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, data-migration, bulk-api, cutover]
model: inherit
effort: high
compatibility: Designed for Claude Code; data extraction, transformation, loading, deletion, and cutover require source, target, privacy, and business-owner approval
---
# Salesforce Governed Data Migration

## Overview

Move data as a controlled accounting exercise in which every source key, transformation, dependency, target result, exception, and rollback obligation is traceable.

## Prerequisites

- Source and target systems, objects, owners, data classes, migration scope, cutover window, and success criteria
- Current source schema, Salesforce metadata, external IDs, relationships, validation, automation, sharing, and limits
- Mapping and transform rules, quality thresholds, quarantine, reconciliation, rollback or compensating action, and retention plan

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Bulk API 2.0 supports asynchronous CSV ingest and query, including insert, update, upsert, and delete where documented and entitled. Data Loader and other tools have separate contracts; object behavior, automation, and limits remain org-specific.

## Authentication

Separate source read, transformation, target write, verification, and support access. Keep tokens and private keys out of migration files; encrypt and expire approved extracts and restrict raw personal data.

## Instructions

1. Freeze scope, source snapshot or watermark, objects, fields, filters, counts, classifications, owners, and cutover criteria.
2. Profile data quality and map source keys, target external IDs, required fields, lookups, parents, children, owners, picklists, and transforms.
3. Discover target API versions, metadata, permissions, sharing, validation, automation, duplicate rules, storage, limits, and lock behavior.
4. Order deterministic migration waves, create immutable manifests and hashes, and separate valid, rejected, and quarantined records.
5. Run dry-run transformations, then small synthetic and representative non-production canaries with full dependency reconciliation.
6. Execute approved production waves within limits; preserve job IDs and result files and never blindly replay uncertain batches.
7. Re-query by stable keys, reconcile counts, values, relationships, ownership, duplicates, and downstream effects; cut over or roll back.

## Approval Boundaries

Do not extract production data, disable automation, change external IDs, overwrite owners, delete records, start a load, or cut over without owners.

## Output

Return scope and snapshot, mappings, quality report, dependency graph, manifests, job results, quarantine, reconciliation, cutover decision, rollback, and expiry.

## Error Handling

| Condition | Response |
|---|---|
| External IDs are not unique | Stop upsert planning and resolve the source and target identity model. |
| Automation changes migrated values | Classify the intended behavior, revise transforms or approved automation, and rerun the canary. |
| Job outcome is incomplete or unavailable | Do not replay; retrieve result evidence and reconcile target keys first. |

## Example

A redacted completion receipt might look like this:

```text
migration=legacy-accounts; source=watermarked; rows=850000; waves=6; success=849920; quarantine=80; reconcile=exact
```

## Resources

- [Bulk API 2.0](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/bulk_api_2_0.htm)
- [Salesforce external IDs](https://help.salesforce.com/s/articleView?id=sf.fields_about_external_ids.htm)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
