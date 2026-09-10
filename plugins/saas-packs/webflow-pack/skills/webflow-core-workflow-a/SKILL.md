---
name: webflow-core-workflow-a
description: >-
  Operate the Webflow CMS staged/live lifecycle with reviewable writes and publishing. Use when creating, updating, publishing, unpublishing, or archiving collection items. Trigger with "manage Webflow CMS", "publish Webflow item", or "sync Webflow content".
argument-hint: "[project-path] [site-id] [collection-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- cms
- publishing
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow CMS Content Lifecycle

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- Staged content is previewable but not necessarily live. Live items can retain unpublished staged changes.
- `isDraft: true` on an already-live item does not unpublish it. Unpublishing uses the live-item unpublish endpoint.
- Individual item publication and site-wide publication are separate operations. Scheduled publication cannot be controlled through the CMS API.
- Archiving retains an item in CMS and removes it from the live site on the next full-site publish; deletion is a different, destructive operation.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Verify site, collection, locale, field schema, and the current staged/live state before constructing changes.
2. Normalize source data against documented field types. Reject unknown fields and preserve item IDs and slugs for rollback.
3. Create or update staged items first. Produce a diff containing item ID, changed fields, prior live state, and intended result.
4. Validate a bounded sample in preview and check references, slugs, locale, asset IDs, and rich-text structure.
5. Ask for explicit approval naming item IDs before publish, unpublish, archive, delete, or site-wide publish.
6. After mutation, re-read the staged and live endpoints and record `isDraft`, `isArchived`, and `lastPublished` evidence.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| Schema validation fails | Stop the batch and report field names and expected Webflow types. |
| Live/staged mismatch | Do not retry a write until the caller chooses which state is authoritative. |
| Partial batch success | Record per-item receipts and retry only failed IDs after reconciliation. |

## Examples

Import three revised articles as staged updates, show their field diffs and preview URLs, obtain approval for those exact item IDs, publish them individually, then verify the live records.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
