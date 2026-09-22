---
name: webflow-enterprise-rbac
description: >-
  Govern enterprise Webflow API access with native scopes, token boundaries, activity evidence, and application authorization. Use when auditing multi-site access or designing least-privilege enterprise operations. Trigger with "Webflow enterprise access", "Webflow audit logs", or "Webflow RBAC".
argument-hint: "[project-path] [workspace-or-site-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- enterprise
- access-control
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow Enterprise Access Governance

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- Webflow scopes authorize API resources; application roles are your application's policy and must not be presented as native Webflow role enforcement.
- Workspace tokens are suited to supported read-only multi-site monitoring and auditing, with workspace-activity scope documented separately.
- Site Activity and Workspace Activity APIs are enterprise surfaces with their own entitlements and scopes.
- Custom-code access requires a Data Client app; site tokens cannot call those endpoints.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Inventory Webflow workspace/site roles, application roles, token types, scopes, service identities, and every protected operation.
2. Create a role-to-operation matrix, then map each operation to exact Webflow endpoints and scopes. Mark application policy versus Webflow enforcement.
3. Use per-site tokens for controlled internal single-site services, OAuth grants for user-authorized multi-site apps, and workspace tokens only for supported workspace reads.
4. Add server-side authorization before API calls and verify the requested site belongs to the authenticated tenant or operator.
5. Collect activity evidence through entitled APIs and your own audit log without storing secret values or sensitive payloads.
6. Test denied operations, cross-site attempts, revoked grants, missing entitlements, and emergency access expiration.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| App role has scope but wrong site | Deny the request; scopes do not replace tenant/site authorization. |
| Activity endpoint forbidden | Verify enterprise entitlement, token type, and the exact activity scope. |
| Native/custom role confusion | Document which control Webflow enforces and which belongs to the application. |

## Examples

A support analyst role may read approved tenant sites through the app, but the server still verifies tenant membership and endpoint scope; a broad OAuth grant alone never authorizes cross-tenant access.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
