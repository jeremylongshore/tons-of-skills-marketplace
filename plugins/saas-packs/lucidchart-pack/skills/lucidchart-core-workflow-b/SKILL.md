---
name: lucidchart-core-workflow-b
description: 'Build and verify a Lucid editor extension that imports or synchronizes governed data. Use when connecting an approved data source to Lucidchart. Trigger with "sync data to Lucidchart".'
argument-hint: "[extension-path] [data-source]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, lucidchart, extension-api, data-sync, integration]
model: inherit
effort: medium
compatibility: Designed for Claude Code; live data access and Lucid publication require owner approval and appropriately scoped credentials
---
# Governed Lucid Data Import and Sync

## Overview
Design an editor extension, and only when required a data connector, that imports or synchronizes approved data without inventing REST endpoints.

## Prerequisites
- A classified source schema, stable record identifiers, and named data owner
- A Lucid developer application and explicit extension scopes
- A reconciliation, deletion, and rollback policy

## Tool Discipline
Use `Read`, `Glob`, and `Grep` to inspect extension code and schemas, `WebFetch` for current Lucid contracts, and `Write` or `Edit` only for local implementation and evidence.

## Current Contract
Lucid documents support data through the Extension API. Data connectors are an optional server-side companion for sources that require OAuth, scheduled updates, or webhook-driven refresh. Consult installed SDK types and official docs rather than guessing namespaces or methods.

## Authentication
Keep source-system credentials server-side. Request the least Lucid extension scopes and OAuth access required. Never place API keys, refresh tokens, or client secrets in extension bundles, logs, fixtures, or document data.

## Instructions
1. Classify the job as one-time import, user-triggered refresh, scheduled sync, or webhook-assisted connector sync.
2. Map source keys, field types, null handling, redaction, row ownership, and conflict policy before writing code.
3. Inspect the installed `lucid-extension-sdk` types and current data-import documentation.
4. Implement a deterministic transform with stable IDs and explicit validation errors.
5. Test against synthetic fixtures, including duplicate, deleted, reordered, and malformed records.
6. Present the intended scopes, data movement, write count, destination, and rollback before live access.
7. After approval, run a bounded canary and reconcile source, Lucid data, visual bindings, and deletions.
8. Record fixture digest, scope set, counts, rejects, drift, and rollback result.

## Approval Boundaries
Do not read production data, register OAuth credentials, publish an extension, or enable scheduled/webhook sync without the responsible owners' approval.

## Output
Return architecture choice, schema map, scopes, fixture results, mutation preview, canary reconciliation, rejects, and rollback evidence.

## Error Handling
| Condition | Response |
|---|---|
| SDK type conflicts with an example | Trust the installed type and current official reference; report the drift. |
| Stable source key is absent | Stop; do not infer identity from mutable display fields. |
| Partial sync occurs | Freeze retries, reconcile by stable ID, and apply the documented conflict policy. |

## Example
```text
mode=user-triggered-refresh; fixture=24; creates=2; updates=5; deletes=0; rejects=1; rollback=verified
```

## Resources
- [Official documentation map](references/official-docs.md)

## Next Steps
Promote the canary only after owner review of data lineage, scopes, reconciliation, and failure recovery.
