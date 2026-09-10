---
name: clickup-multi-env-setup
description: >-
  Separate ClickUp development, staging, and production identities, Workspaces, callbacks, queues, and data with fail-closed guards. Use when one integration spans multiple environments. Trigger with "ClickUp environments", "ClickUp staging setup", or "ClickUp tenant isolation".
argument-hint: "[repository-path] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- environment-management
model: inherit
effort: high
compatibility: Designed for Claude Code; each live environment requires separately governed ClickUp authorization
---
# ClickUp Multi-Environment Isolation

## Overview

Prevent a development process or callback from crossing into production merely because a shared token can access multiple Workspaces.

## Prerequisites

- An environment matrix of OAuth apps or personal tokens, allowed Workspace IDs, callback URLs, queues, and secret references
- Separate non-production data and synthetic verification records
- Deployment and incident owners for every environment

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- OAuth users can authorize one or more Workspaces, so the application must enforce its own environment allow-list.
- Redirect URIs and webhook endpoints are environment-specific and HTTPS.
- Rate limits are per token; sharing a token also shares its budget and blast radius.
- v2 team IDs and v3 Workspace IDs must resolve to the same intended environment boundary.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Inventory every environment's credentials, app IDs, redirects, webhooks, queues, storage, and Workspace IDs.
2. Remove shared credentials and assign an accountable owner and rotation path to each secret.
3. Implement startup and per-request guards that compare environment and Workspace allow-lists.
4. Namespace reconciliation keys, queues, metrics, and callback secrets by environment.
5. Run offline cross-environment denial tests and bounded live identity/Workspace probes.
6. Publish the matrix and fail deployment if any production boundary is ambiguous.

## Approval Boundaries

Do not reuse production credentials or data in lower environments, authorize extra Workspaces silently, or copy production webhook secrets.

## Output

Return the environment matrix, shared-boundary findings, guard/test results, live Workspace matches, and unresolved isolation risks.

## Error Handling

| Condition | Response |
|---|---|
| One token spans conflicting environments | Disable writes and replace it with separated identities. |
| Workspace ID is not allow-listed | Reject the operation. |
| Callback points to another environment | Do not deploy or register the webhook. |
| Secret owner is unknown | Block promotion until ownership is assigned. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
env=staging; workspace-match=yes; shared-secrets=0; cross-env-tests=pass; writes=disabled
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [API availability by plan](https://developer.clickup.com/docs/apis-available-by-plan)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
