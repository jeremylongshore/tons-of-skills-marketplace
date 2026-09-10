---
name: clickup-ci-integration
description: >-
  Gate ClickUp adapters with offline OpenAPI contracts and a protected read-only live probe. Use when adding CI for a ClickUp-backed repository. Trigger with "ClickUp CI", "test ClickUp integration", or "ClickUp contract tests".
argument-hint: "[repository-path] [live-test-environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- ci
model: inherit
effort: high
compatibility: Designed for Claude Code; a live lane requires a protected non-production ClickUp credential
---
# ClickUp Continuous Integration

## Overview

Keep ordinary pull-request checks deterministic and secretless while retaining a separately protected probe for provider-contract drift.

## Prerequisites

- The repository's test runner, ClickUp transport boundary, and CI platform
- Sanitized fixtures for v2 and any selected v3 response shapes
- A protected non-production credential and strict request ceiling for the optional live lane

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- Pin the official v2 and v3 OpenAPI inputs separately; do not model v3 as a complete replacement.
- Offline tests cover authentication, plan denial, pagination, rate headers, webhook typing, and redaction.
- The live lane uses `GET /api/v2/user` or `GET /api/v2/team`; it does not create or update work.
- Fork code never receives ClickUp credentials.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Inventory every endpoint, version, fixture, secret reference, and network-bearing test.
2. Generate or validate transport types against pinned official OpenAPI inputs.
3. Add fixtures for success, common OAuth errors, 429 responses, null webhook fields, and page boundaries.
4. Test redaction, retry eligibility, version routing, and workspace allow-list enforcement.
5. Place the bounded live probe behind a trusted event and protected environment.
6. Publish status, schema versions, request count, and redacted drift evidence.

## Approval Boundaries

Do not expose credentials to fork code or let CI create tasks, webhooks, members, ACLs, or hierarchy objects without a separate environment approval and cleanup plan.

## Output

Return offline coverage, pinned schema digests, live-lane eligibility/result, workspace boundary, request count, and any provider drift.

## Error Handling

| Condition | Response |
|---|---|
| No approved live credential | Skip the live probe and keep offline contracts authoritative. |
| Fork event requests secrets | Refuse the secret-bearing job. |
| OpenAPI version drifts | Fail visibly and review the endpoint-specific delta. |
| Credential appears in logs | Cancel the run, rotate or revoke it, and scrub artifacts. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
offline=pass; v2_schema=pinned; v3_schema=pinned; live=skipped(untrusted-event); writes=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [OpenAPI specifications](https://developer.clickup.com/docs/open-api-spec)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
