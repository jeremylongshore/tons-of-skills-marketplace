---
name: webflow-common-errors
description: >-
  Diagnose Webflow Data API failures using the returned HTTP status and structured error body. Use when requests fail with 4xx, 429, or 5xx responses. Trigger with "Webflow error", "Webflow 403", or "Webflow API failed".
argument-hint: "[project-path] [status-or-code]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- debugging
- errors
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow API Error Diagnosis

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- Webflow error bodies expose `code`, `message`, `externalReference`, and `details`; preserve those fields after redaction.
- 400 is malformed input, 401 lacks valid authentication, 403 lacks permission, 404 misses the resource, and 409 conflicts with current state.
- 429 responses should honor `Retry-After`; official SDKs include exponential backoff.
- 5xx errors can be transient, but retries must be bounded and idempotent. Never replay an uncertain write blindly.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Capture the operation, endpoint family, HTTP status, Webflow code, request ID or headers, and a redacted error body.
2. Reproduce with the smallest read-only request using the same client configuration; do not paste bearer tokens into shell history.
3. Check site/resource IDs and staged/live or locale selection before changing authentication.
4. For 401/403, compare token type and exact endpoint scope. Rotate only when revocation or compromise is established.
5. For 429/5xx, classify read versus write, honor retry guidance, add jitter, and stop after a bounded attempt count.
6. Return a diagnosis with evidence, a minimal correction, and an explicit statement of whether any prior write may have succeeded.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| 400 `bad_request` | Validate field names and types against the exact endpoint schema. |
| 409 `conflict` | Re-read current state and design an idempotent reconciliation. |
| Unknown 5xx write result | Check the resource before retrying to avoid a duplicate mutation. |

## Examples

For a 403 from a custom-code call, preserve the structured error, confirm the caller uses a site token, identify the token-type limitation, and recommend a Data Client app instead of broadening random scopes.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
