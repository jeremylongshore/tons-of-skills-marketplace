---
name: bamboohr-core-workflow-a
description: >-
  Build a permission-aware BambooHR employee and dataset synchronization
  workflow with pagination, field minimization, and checkpoints. Use when
  exporting employee changes or replacing deprecated report calls. Trigger with
  "sync BambooHR employees", "BambooHR dataset", or "BambooHR HR pipeline".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<dataset-or-employee-scope> <destination>"
version: 1.5.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, hr, bamboohr, employees, data-sync]
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# BambooHR Employee and Dataset Sync

## Overview

Design a resumable read pipeline for employee data. Prefer BambooHR's dataset v2
contract for new bulk data work, minimize fields at the source, and treat missing
fields as a possible permission decision rather than automatically as data loss.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The tenant, identity, and data scope only when approved live work is in scope.
- The current evidence register plus customer-specific permissions and agreements.

## Current Contract

- Employee endpoints include list, get, create, and update operations.
- `POST /api/v2/datasets/{datasetName}/data` accepts `fields`, OData-style
  `filter`, `orderBy`, `page`, and `pageSize` and returns `data`, `links`, and
  `meta`; page size is at most 1000 in the reviewed OpenAPI.
- Dataset v1 data calls are deprecated. Dataset discovery and field discovery
  use v1.2 endpoints in the current OpenAPI.
- Legacy custom-report endpoints carry deprecation notices. Do not start a new
  pipeline on them merely because old examples do.

## Authentication

Use OAuth scope `report` where the documented dataset operation requires it, or
a dedicated API-key user with access only to selected fields. Bind credentials,
checkpoint, and destination namespace to one tenant.

## Instructions

1. Define the business purpose, legal basis, tenant, destination, data owner,
   refresh target, and exact employee fields before making a request.
2. Discover the dataset and its field definitions from current endpoints. Save
   field IDs and semantic mappings as reviewed configuration, not assumptions.
3. Query dataset v2 with deterministic ordering. Keep every ordered field in the
   requested `fields` list and bound `pageSize` to the documented maximum.
4. Follow returned pagination metadata or links until completion. Persist a
   checkpoint only after the destination transaction commits.
5. Upsert by a stable tenant-scoped employee identifier. Distinguish absent,
   null, redacted, future-dated, and inactive values.
6. Reconcile source count, received count, accepted count, rejected count, and
   destination count. Quarantine schema or permission drift instead of deleting.
7. Encrypt retained HR data and delete raw page bodies after the approved
   retention window.

## Tool Discipline

Use Read, Glob, and Grep to inspect mappings, schemas, and checkpoints. Use
Write/Edit only for approved pipeline code, configuration, and tests. Do not use
this skill to fetch production employee data or mutate a downstream system.

## Approval Boundaries

Require approval for the field set, inactive/future employee inclusion,
production tenant, destination, retention policy, and any employee create or
update operation. Reads do not authorize writes.

## Output

Return dataset and field selection, auth identity, pagination and checkpoint
design, mapping contract, reconciliation counts, retention controls, tests, and
all unapproved live operations.

## Error Handling

- `403`: re-check field-level permission and requested dataset; do not request
  broader access without a business owner.
- `413`: reduce page size or field set; never silently drop records.
- `422`: reject the invalid filter/order contract and preserve the checkpoint.
- Missing field with `200`: compare requested and returned schemas because some
  report paths omit inaccessible fields without failing.

## Examples

- "Sync active employees to the warehouse" produces a minimized dataset v2 plan.
- "Copy every employee field" pauses for field necessity and retention approval.

## Resources

Read [official evidence](references/official-docs.md) before selecting endpoints.
