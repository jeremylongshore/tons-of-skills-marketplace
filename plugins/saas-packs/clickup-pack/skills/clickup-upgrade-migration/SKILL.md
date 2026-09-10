---
name: clickup-upgrade-migration
description: >-
  Migrate ClickUp endpoints, schemas, clients, and terminology with version inventory, dual contracts, canaries, and rollback. Use when adopting selected API v3 surfaces or provider changes. Trigger with "upgrade ClickUp API", "ClickUp v3 migration", or "ClickUp schema change".
argument-hint: "[repository-path] [target-endpoint-or-version]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- upgrade
model: inherit
effort: high
compatibility: Designed for Claude Code; live canaries require authorized non-production ClickUp access
---
# ClickUp API Evolution Migration

## Overview

Evolve endpoint-by-endpoint because ClickUp v2 remains the primary surface while selected capabilities use v3. Never infer a platform-wide cutover from one migrated endpoint.

## Prerequisites

- An inventory of every endpoint, version, field assumption, pagination loop, and webhook dependency
- Pinned current/target OpenAPI schemas and representative sanitized fixtures
- Feature flags, canary environment, reconciliation, and rollback ownership

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- There is no general v2-to-v3 cutover contract; preserve explicit version routing for unchanged v2 operations.
- v2 uses Team for Workspace while v3 uses Workspace; Groups remain user groups.
- Different endpoints can have different pagination and response types, so a base-path swap is unsafe.
- Preview or experimental surfaces require tighter pins and rollback.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Inventory current operations and label each v2, v3, deprecated, preview, or unknown.
2. Diff official schemas and docs for path, auth, plan, parameter, field, pagination, and error changes.
3. Update typed adapters behind a feature flag while preserving the current path.
4. Run offline dual-contract fixtures and migration tests, including nulls and partial failures.
5. Canary read-only traffic, then separately approved synthetic writes, and compare normalized results.
6. Promote endpoint-by-endpoint or roll back; update evidence and remove old code only after stability.

## Approval Boundaries

Do not globally replace `/api/v2`, silently coerce fields, auto-fallback writes, or remove the rollback path before the stability window.

## Output

Return operation inventory, schema delta, compatibility decisions, test/canary results, rollout state, rollback, and unresolved risks.

## Error Handling

| Condition | Response |
|---|---|
| Target endpoint is not generally available | Keep the current path and record the prerequisite. |
| Normalized results differ | Stop promotion and investigate semantics. |
| Rollback data is incomplete | Do not enable writes. |
| Terminology change alters tenant routing | Fail closed on Workspace mismatch. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
target=v3-auditlogs; v2-operations-retained=14; schema-tests=pass; read-canary=pass; write-canary=not-applicable
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [API v2 and v3 terminology](https://developer.clickup.com/docs/general-v2-v3-api)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
