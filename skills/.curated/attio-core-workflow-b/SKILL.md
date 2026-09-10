---
name: attio-core-workflow-b
description: >-
  Build an Attio workflow around lists and entries while keeping record data, list-specific attributes, notes, and tasks correctly separated. Use when implementing pipelines, queues, or operational CRM processes. Trigger with "Attio lists", "Attio entries", or "Attio pipeline workflow".
argument-hint: "[repository-path] [list-slug] [workflow]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- attio
- lists
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# Attio Lists and Entries Workflow

## Overview

This skill models a business process without confusing an Attio record with its membership in a list. It makes ownership of record attributes and entry attributes explicit.

## Prerequisites

- A named list slug or UUID and its permitted parent object
- Current list attribute definitions
- Stable parent record IDs
- Required list-entry, note, or task scopes for the selected workflow

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect process rules, identifiers, mappings, and tests. Use `WebFetch` only for current official Attio documentation. Use `Write` or `Edit` after the list contract and mutation boundary are confirmed.

## Current Contract

- A list entry points to one parent record and carries list-specific values.
- Removing an entry from a list is not the same as deleting its parent record.
- Entry query and pagination rules come from the exact endpoint reference.
- Notes and tasks are separate resources; do not store their content in list attributes as a shortcut.

## Authentication

Use Bearer authentication with only the read or read-write scopes needed for list configuration, entries, notes, tasks, and parent records. Resolve 403 responses from endpoint scope documentation.

## Instructions

1. Resolve the list and confirm its parent object and attribute definitions.
2. Query existing entries to determine whether the parent record is already present.
3. Add the parent record only when membership does not exist; persist the returned entry ID.
4. Update only integration-owned entry attributes using the endpoint's documented update semantics.
5. Create notes or tasks only when they are part of the approved workflow and link them to exact records.
6. Read the entry back and verify parent identity, owned values, and process state.
7. For removal, delete only the entry unless parent-record deletion is separately approved.

## Approval Boundaries

Bulk entry changes, task assignment, destructive removal, and any parent-record deletion require a preview of exact IDs and impact. Never treat a list slug as sufficient proof of record identity.

## Output

Return the list schema, parent-object check, membership decision, changed values, linked-resource IDs, verification result, and cleanup disposition.

## Error Handling

| Condition | Response |
|---|---|
| Parent object is incompatible | Stop and choose the correct list or record. |
| Membership already exists | Reuse its entry ID; do not create a duplicate. |
| Entry and record values conflict | Apply the documented ownership boundary. |
| Removal intent is unclear | Refuse mutation and show entry versus record impact. |

## Examples

Input:

```text
list=sales-pipeline; parent=company-id; owned-entry-fields=stage,owner
```

Expected handoff:

```text
membership=existing; update=verified; parent-record=preserved
```

This result shows that the list workflow changed only its owned entry values.

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Objects and lists](https://docs.attio.com/docs/objects-and-lists)
- [Pagination](https://docs.attio.com/rest-api/guides/pagination)
- [REST API overview](https://docs.attio.com/rest-api/overview)
