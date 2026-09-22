---
name: webflow-upgrade-migration
description: >-
  Upgrade Webflow SDK, Data API, or CLI integrations with contract evidence and rollback. Use when leaving Data API v1, updating the official JavaScript SDK, or migrating Webflow CLI 1.x scripts. Trigger with "upgrade Webflow SDK", "migrate Webflow v1", or "Webflow CLI 2".
argument-hint: "[project-path] [current-version] [target-version]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- migration
- sdk
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow SDK and API Upgrade

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- Data API v2 is the default current contract; use Webflow's migration guide and exact endpoint references rather than a memorized method map.
- SDK package versions and generated method names change independently from your application adapter; inspect the installed and target package types.
- Webflow CLI 2.x requires Node.js 22.13.0 or newer and renames documented commands while retaining deprecated aliases temporarily.
- CLI app-management commands may require the `next` channel even when stable Cloud commands exist; record the exact installed channel and version.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Inventory API hosts, headers, SDK imports, generated methods, CLI commands, Node version, scopes, and staged/live assumptions.
2. Pin current and target versions and read their official migration notes. Build a call-site matrix with old contract, new contract, and test coverage.
3. Add characterization tests around pagination, errors, CMS state, locale behavior, webhook verification, and write idempotency.
4. Upgrade the adapter on a branch, then fix callers from compiler and test evidence rather than mass search-and-replace.
5. Run read-only integration smoke tests against a non-production site; preview any changed write payloads.
6. Obtain approval before production rollout and retain the prior lockfile, deployment artifact, and data reconciliation plan.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| Method missing | Inspect target SDK types and endpoint docs; update the adapter deliberately. |
| CLI command unknown | Check stable versus `next` channel and the CLI 2 migration table. |
| Behavioral drift | Roll back the dependency or deployment, preserve fixtures, and isolate the changed contract. |

## Examples

For a Data API v1 service, first inventory endpoints and scopes, add characterization fixtures, move one adapter to v2, verify staged/live behavior on a test site, and only then roll out with the old lockfile retained.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
