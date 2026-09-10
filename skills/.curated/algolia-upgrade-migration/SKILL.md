---
name: algolia-upgrade-migration
description: >-
  Migrate an Algolia JavaScript client integration from v4 to v5 with inventory, compatibility tests, and rollback. Use when removing initIndex, updating client methods, or reconciling mixed major versions. Trigger with "upgrade Algolia v5", "remove initIndex", or "Algolia SDK migration".
argument-hint: "[repository-path] [package-name]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- upgrade
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia JavaScript v4 to v5 Upgrade

## Overview

This skill follows the official v5 migration contract and the repository's pinned dependency graph. It treats import, method, parameter, response, wait, and test changes as one controlled migration.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Version 5 removes `initIndex`; methods live on the client and receive `indexName`.
- Upgrade search-only imports and multi-search calls according to the official guide, not a mechanical rename.
- Replace chained write waits with the documented v5 wait helpers and retain task IDs.
- Check all Algolia packages, frameworks, wrappers, mocks, generated types, and examples for major-version coupling.

## Authentication

Do not change key privilege during an SDK upgrade. Use existing least-privilege test credentials only for safe verification targets.

## Instructions

1. Inventory package versions, imports, `initIndex`, client wrappers, methods, waits, mocks, and runtime targets.
2. Read the current official v5 migration guide and installed types for every used method.
3. Update the dependency and lockfile through the repository's package manager.
4. Migrate one boundary at a time, adapting parameters, responses, tasks, and errors.
5. Run type, unit, integration, build, and representative query tests; use a disposable index for writes.
6. Record compatibility gaps, final versions, release notes, rollback commit, and follow-up cleanup.

## Approval Boundaries

Do not combine the SDK upgrade with relevance, index schema, credential, or broad architectural changes unless separately scoped and tested.

## Output

Return the usage inventory, official mapping, dependency diff, migrated boundaries, test evidence, remaining v4 patterns, compatibility notes, and rollback.

## Error Handling

| Condition | Response |
|---|---|
| `initIndex` remains | Locate the call or generated artifact and migrate it. |
| Method signature differs | Follow installed v5 types and current official reference. |
| Mock passes but live test fails | Correct the application adapter contract. |
| Rollback changes lockfile only | Revert source and lockfile as one unit. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
from=algoliasearch-4; to=pinned-5; initIndex-calls=9; wrappers=2
```

Expected handoff:

```text
initIndex=0; typecheck=pass; integration=pass; disposable-write-cleaned=yes
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [JavaScript v5 upgrade](https://www.algolia.com/doc/libraries/sdk/upgrade/javascript)
- [JavaScript API client](https://www.algolia.com/doc/libraries/javascript)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
