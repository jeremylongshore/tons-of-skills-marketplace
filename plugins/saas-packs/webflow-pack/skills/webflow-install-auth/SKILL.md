---
name: webflow-install-auth
description: >-
  Install or repair a Webflow Data API integration and choose the correct bearer-token model. Use when bootstrapping the official SDK, narrowing scopes, or diagnosing token setup. Trigger with "install Webflow", "configure Webflow auth", or "choose a Webflow token".
argument-hint: "[project-path] [site-token|workspace-token|oauth]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- authentication
- oauth
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow Install and Authentication

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- Webflow Data API v2 accepts bearer tokens. Site tokens are for one site, workspace tokens are intended for read-only multi-site monitoring or auditing, and OAuth is for user-authorized or marketplace apps.
- Site tokens expire after 365 consecutive inactive days, a site can have up to five, and site tokens cannot call authorization, custom-code, or workspace-activity endpoints.
- Scopes are resource-specific. Determine them from the exact endpoints; do not copy a broad canned scope list.
- The official JavaScript SDK package is `webflow-api`. Resolve and pin the version from the target lockfile instead of embedding a floating `latest` command.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Classify the integration as single-site internal automation, read-only workspace monitoring, or a user-authorized app. Record the decision and excluded token types.
2. Inspect manifests, lockfiles, environment schemas, and existing clients. Identify the installed SDK and Data API version before editing.
3. Build an endpoint-to-scope table from the current official endpoint pages. Request read scopes unless a named write operation is required.
4. Store only environment-variable names and secret-manager references in source. Add `.env*` exclusions without creating sample values that resemble credentials.
5. Initialize one server-side client and add a read-only connection check such as listing the sites visible to the token.
6. Verify that the returned site or workspace identity matches the intended environment, then document revocation and rotation ownership.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| 401 `not_authorized` | Check bearer-header construction, token revocation, and inactive-token expiry; do not print the token. |
| 403 `forbidden` | Compare the endpoint's documented scope and token-type limitations with the issued token. |
| Unexpected sites | Stop: the token belongs to the wrong workspace or environment; do not continue to writes. |

## Examples

For an internal single-site CMS reader, select a site token with `cms:read`, keep the token in the deployment secret store, verify the intended site ID, and leave all write scopes absent.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
