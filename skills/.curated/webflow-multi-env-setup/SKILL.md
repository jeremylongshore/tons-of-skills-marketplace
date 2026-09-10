---
name: webflow-multi-env-setup
description: >-
  Separate Webflow development, staging, and production identities, tokens, sites, and release policy. Use when preventing cross-environment writes or configuring environment-aware CI. Trigger with "Webflow environments", "Webflow staging", or "separate Webflow tokens".
argument-hint: "[project-path] [dev|staging|production]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- environments
- configuration
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow Multi-Environment Setup

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- Site IDs are identifiers, not secrets, but they still must be verified and allowlisted to prevent cross-environment writes.
- `WEBFLOW_API_TOKEN` is a read-only CLI input and is not resolved from `webflow.json`; app and environment IDs have documented resolution precedence.
- Flags override environment variables and manifest values. CI should pass target IDs explicitly even when a manifest exists.
- Separate sites and least-privilege tokens provide stronger isolation than naming conventions alone.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Inventory every environment, Webflow site/app/environment/workspace ID, domain, token owner, scope set, and deployment branch.
2. Create a typed mapping that requires an explicit environment and rejects unknown or mismatched IDs.
3. Store secret values only in the environment's secret manager; keep non-secret manifest IDs reviewed and versioned where appropriate.
4. Add guards that print target names and IDs—not secrets—and require production confirmation before live writes.
5. Use development fixtures and a staging site for integration tests; prohibit production fallbacks.
6. Verify each environment read-only and document promotion, rollback, token rotation, and emergency freeze procedures.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| Environment omitted | Fail closed; never default a mutating workflow to production. |
| Token sees wrong site | Revoke or re-scope it and correct the identity mapping before further calls. |
| Manifest/flag conflict | Treat the explicit flag as active, surface both values, and require reconciliation. |

## Examples

A three-stage CMS service uses separate sites and tokens, passes the production site ID explicitly in protected CI, prints the verified target, and requires approval before publication.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
