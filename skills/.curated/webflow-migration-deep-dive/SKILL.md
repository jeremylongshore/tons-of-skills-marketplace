---
name: webflow-migration-deep-dive
description: >-
  Migrate external or cross-site content into Webflow CMS with schema mapping, staged batches, reconciliation, and controlled publication. Use when moving WordPress, CSV, JSON, or Webflow-to-Webflow content. Trigger with "migrate to Webflow", "bulk import Webflow", or "move Webflow CMS".
argument-hint: "[project-path] [source] [site-id] [collection-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- migration
- cms
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow Content Migration

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- Migration should target staged CMS content first; publication is a distinct operation with separate approval.
- Field types, references, assets, locales, slugs, draft state, and archive state must be mapped explicitly.
- Bulk limits and response shapes are endpoint-specific. Read the current create/update/publish endpoint instead of assuming a universal batch size.
- Webflow has no universal transaction rollback for a migration; preserve source snapshots, ID maps, and compensating unpublish/archive/delete plans.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Freeze and export the source with a checksum, record counts, identifiers, relationships, locales, assets, and content status.
2. Inspect target collection schemas and build an explicit source-to-Webflow field map with transformations and rejection rules.
3. Create a deterministic ID/slug map and validate a small fixture set without contacting production.
4. Import a bounded canary into staged state, preserving per-record receipts and never publishing automatically.
5. Compare counts, field values, references, asset availability, locales, and preview output; reconcile failures before the next batch.
6. After explicit approval naming the collection and item set, publish in bounded groups and verify live state; retain source and mapping evidence through the rollback window.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| Field/reference mismatch | Quarantine the record and fix the map; do not coerce silently. |
| Partial batch result | Record successful item IDs and retry only reconciled failures. |
| Live validation fails | Stop publication and use the approved unpublish or prior-content recovery plan. |

## Examples

For a WordPress export, checksum the source, map authors and categories to Webflow references, import ten staged posts, validate previews and counts, then request approval before publishing those exact item IDs.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
