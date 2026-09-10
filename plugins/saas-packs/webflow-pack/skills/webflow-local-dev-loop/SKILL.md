---
name: webflow-local-dev-loop
description: >-
  Create a repeatable local loop for a Webflow Data API, Cloud app, or Designer extension. Use when setting up local development, fixtures, typechecking, or non-production smoke tests. Trigger with "Webflow local dev", "test Webflow locally", or "mock Webflow API".
argument-hint: "[project-path] [data-api|cloud|extension]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- development
- testing
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow Local Development Loop

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- Webflow CLI 2.x requires Node.js 22.13.0 or newer. Detect the installed version rather than silently upgrading it.
- Data API services, Webflow Cloud apps, and Designer extensions have different local commands and authentication boundaries; classify the project before scaffolding.
- CLI `apps` management commands are currently on `@webflow/webflow-cli@next`; stable CLI covers the documented stable surfaces.
- Tests should use fixtures or a dedicated non-production site. A developer token must never silently fall through to production.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Inventory the project and classify its Webflow surface from imports, `webflow.json`, scripts, and API hosts.
2. Record Node, package manager, SDK, and CLI versions. Pin the exact versions used by CI.
3. Create an environment schema that rejects a production site ID in local mode and never supplies fallback token values.
4. Capture representative API responses as redacted fixtures, preserving status, pagination, staged/live state, and locale shape.
5. Add unit tests for mapping and error handling plus an opt-in integration test against a named development site.
6. Document one fast loop: typecheck, unit test, local run, and optional integration smoke. Keep tunnels and public callbacks opt-in and time-bounded.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| CLI command missing | Check whether the command is stable or requires the documented `next` channel. |
| Node too old | Stop and report the required CLI runtime; do not mutate the system runtime automatically. |
| Production ID detected | Fail closed and require a separate environment configuration. |

## Examples

For a CMS sync service, use redacted staged/live fixtures in unit tests and gate the real integration test behind an explicit development-site ID and token.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
