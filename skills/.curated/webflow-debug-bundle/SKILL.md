---
name: webflow-debug-bundle
description: >-
  Collect a redacted Webflow integration evidence bundle for troubleshooting or support. Use when an incident needs reproducible versions, identities, headers, and error context without secret leakage. Trigger with "Webflow debug bundle", "collect Webflow evidence", or "Webflow support ticket".
argument-hint: "[project-path] [incident-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- debugging
- support
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow Debug Evidence Bundle

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- A useful bundle identifies the SDK and CLI versions, API host, endpoint family, site ID, status, Webflow error code, and rate-limit headers.
- Tokens, OAuth codes, webhook secrets, authorization headers, form values, and ecommerce customer data must never enter the bundle.
- Content Delivery responses expose `cf-cache-status`; Data API responses expose rate-limit headers relevant to diagnosis.
- Bundle collection must be read-only. Token rotation, webhook replacement, and publishing are remediation actions, not diagnostics.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Inventory package manifests, lockfiles, `webflow.json`, environment-variable names, client construction, and recent relevant logs.
2. Extract versions and configuration names without reading or printing secret values.
3. Collect a minimal failed request description, structured error fields, response headers, timestamps, and retry count.
4. Record expected and observed site, collection, item, locale, and staged/live identities.
5. Redact secrets and personal data, then review the final bundle for authorization headers, tokens, emails, phones, addresses, and order data.
6. Package only after the user confirms the destination and retention policy; otherwise leave a local redacted report.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| Secret detected | Stop packaging, redact the value and nearby context, then rescan. |
| No reproducible request | Document the gap and collect application-side correlation evidence. |
| Bundle too broad | Reduce it to the failing integration and time window. |

## Examples

For intermittent 429s, collect the SDK version, endpoint class, timestamps, `X-RateLimit-*` and `Retry-After` headers, shared-worker count, and redacted error bodies—never the bearer token.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
