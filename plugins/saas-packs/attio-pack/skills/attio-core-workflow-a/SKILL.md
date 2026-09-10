---
name: attio-core-workflow-a
description: >-
  Implement a safe Attio record lifecycle for standard or custom objects, including schema discovery, query, create or assert, update, and delete controls. Use when building record synchronization or CRM write paths. Trigger with "Attio records", "Attio CRUD", or "sync Attio objects".
argument-hint: "[repository-path] [object-slug] [operation]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- attio
- records
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# Attio Record Lifecycle

## Overview

This skill builds a record workflow from the workspace's actual object and attribute schema. It favors deterministic identity and reversible updates over blind create calls.

## Prerequisites

- A named object slug or UUID and the target workspace
- Current attribute definitions for that object
- A stable matching attribute for assert or deduplication
- An approved write and deletion boundary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the local data model, mapping code, tests, and request wrapper. Use `WebFetch` only for current official Attio documentation. Use `Write` or `Edit` after the object contract and approval boundary are explicit.

## Current Contract

- Objects define attributes; records are instances of an object.
- Record values are shaped by each attribute type, not by one universal scalar rule.
- Query records with `POST /v2/objects/:object/records/query`; this endpoint uses `limit` and `offset`.
- Choose create versus assert deliberately. Assert is appropriate only when a documented matching attribute supplies stable identity.
- `PUT` and `PATCH` have different multiselect behavior; confirm the endpoint reference before updating.

## Authentication

Send a single-workspace or OAuth access token as `Authorization: Bearer <access_token>`. Confirm the endpoint's object-configuration and record-permission scopes before any write.

## Instructions

1. Resolve the object and fetch its current attribute definitions.
2. Map source fields to exact attribute slugs and value shapes; reject unknown mappings.
3. Choose query, create, or assert based on the integration's identity policy.
4. For updates, state whether multiselect values must be overwritten or appended and select the documented method.
5. Persist the Attio record ID and source identity mapping after a successful write.
6. Read the record back and compare only the fields owned by this integration.
7. Require explicit approval before deletion and verify the exact record identity afterward.

## Approval Boundaries

Never infer a destructive target from a display name. Record deletion, bulk writes, schema changes, and overwrite updates require the exact workspace, object, record IDs, and owner approval.

## Output

Return the schema snapshot, identity rule, request plan, redacted response evidence, read-after-write comparison, and rollback or cleanup status.

## Error Handling

| Condition | Response |
|---|---|
| Attribute slug is absent | Stop and refresh object definitions. |
| Assert matches unexpectedly | Stop; reconcile the matching attribute and source identity. |
| Multiselect result is wrong | Check `PUT` versus `PATCH` semantics before retrying. |
| Delete target is ambiguous | Refuse deletion and return candidate IDs for review. |

## Examples

Input:

```text
object=companies; operation=assert; match=domains; owned-fields=description,domains
```

Expected handoff:

```text
schema=confirmed; identity=stable; write=verified; foreign-fields=untouched
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Objects and lists](https://docs.attio.com/docs/objects-and-lists)
- [List records](https://docs.attio.com/rest-api/endpoint-reference/records/list-records)
- [OpenAPI specification](https://docs.attio.com/rest-api/endpoint-reference/openapi)
