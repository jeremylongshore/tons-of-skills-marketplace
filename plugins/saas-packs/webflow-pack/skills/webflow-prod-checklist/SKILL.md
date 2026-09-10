---
name: webflow-prod-checklist
description: >-
  Gate a Webflow integration before production with identity, scope, retry, privacy, rollout, and rollback evidence. Use when preparing to enable live traffic or live content writes. Trigger with "Webflow production checklist", "ship Webflow integration", or "Webflow go live".
argument-hint: "[project-path] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- production
- reliability
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow Production Readiness

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- Production readiness depends on the exact token type, endpoint scopes, site IDs, staged/live workflow, and plan limits—not a generic green health check.
- Readiness must test 401/403/429/5xx handling and uncertain-write reconciliation.
- CMS publish, unpublish, archive, delete, site publish, webhook replacement, and Cloud deploy are distinct live mutations.
- A rollback plan must name recoverable artifacts and compensating actions; Webflow does not provide a universal transaction rollback.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Freeze the release candidate and record dependency, SDK, CLI, schema, and configuration versions.
2. Verify production site and collection allowlists, token type, minimal scopes, secret ownership, and log redaction.
3. Exercise read-only smoke tests and failure-path tests against fixtures or a dedicated staging site.
4. Create a release plan listing every live mutation, target ID, expected result, validation query, and compensating action.
5. Obtain explicit approval for the named production targets, then execute one bounded canary if mutation was requested.
6. Verify live state, rate-limit headroom, webhook delivery, and monitoring; stop rollout on any mismatch.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| Identity mismatch | Stop before mutation and correct the environment mapping. |
| Canary differs from preview | Pause rollout, preserve evidence, and reconcile staged/live state. |
| Rollback cannot be demonstrated | Do not approve the release; define restore data or compensating operations first. |

## Examples

Before a CMS launch, verify the production site allowlist and scopes, stage one canary item, approve that item ID, publish it, confirm the live representation and webhook, then continue in bounded batches.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
