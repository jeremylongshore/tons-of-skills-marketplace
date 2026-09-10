---
name: webflow-core-workflow-b
description: >-
  Plan Webflow Data API operations outside the core CMS item loop, including pages, components, forms, ecommerce, assets, and custom code. Use when a request spans site resources or needs endpoint-specific scope review. Trigger with "Webflow site API", "Webflow forms", or "Webflow ecommerce".
argument-hint: "[project-path] [site-id] [resource]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- data-api
- operations
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow Site and Extended Data Operations

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- Pages, components, forms, ecommerce, assets, custom code, and sites have separate endpoint families and scope pairs.
- Custom-code scopes are available to Data Client apps; site tokens cannot access custom-code endpoints.
- Form submissions and ecommerce records can contain personal or financial-adjacent data and require minimization before logs or fixtures.
- Site publishing is a separate write with an endpoint-specific limit and must not be coupled automatically to unrelated updates.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Classify the requested resource and operation; reject a kitchen-sink implementation plan that mixes unrelated writes.
2. Open the exact endpoint reference and record method, path, token eligibility, required scope, request fields, and pagination.
3. Inventory existing adapters and reuse their identity, error, retry, and redaction contracts.
4. Build a read-only probe first and verify the site and resource IDs returned.
5. For writes, produce a resource-specific diff and rollback or compensating action. Require explicit approval for the exact target.
6. Verify by re-reading the resource and report any downstream publish step separately.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| 403 on custom code | Confirm the integration is a Data Client app; a site token is not eligible. |
| Sensitive form/order payload | Redact and minimize before storing diagnostics or fixtures. |
| Publish needed | Present it as a separate approval boundary after the resource update verifies. |

## Examples

For a page metadata correction, inspect the page endpoint and `pages:write` requirement, diff only the requested metadata, obtain approval, patch that page, and verify without publishing the whole site automatically.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
