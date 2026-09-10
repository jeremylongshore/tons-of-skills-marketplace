---
name: algolia-install-auth
description: >-
  Install and verify the Algolia JavaScript v5 client with least-privilege credential separation. Use when bootstrapping a backend, browser search client, or environment configuration. Trigger with "install Algolia", "configure Algolia auth", or "Algolia API key setup".
argument-hint: "[project-path] [runtime]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- authentication
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Install and Authentication

## Overview

This skill establishes the package and credential boundary before feature work. It distinguishes the application ID from API keys and separates browser search from trusted write operations.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Inspect and follow the repository's package manager and lockfile rather than installing an unpinned latest package.
- Use `algoliasearch` v5 imports and client-level methods; do not introduce the removed `initIndex` pattern.
- Expose only a search-only or appropriately secured key in browser configuration.
- Use custom keys with minimum ACLs and index restrictions for backend jobs.

## Authentication

Load credentials through the repository's approved secret mechanism. Never print values, commit `.env` files, or use the Admin key as the default backend credential.

## Instructions

1. Inspect runtime, package manager, lockfile, existing wrappers, and environment conventions.
2. Select a compatible pinned v5 version and add it through the native package workflow.
3. Define separate environment names for application ID, browser search key, and server write key.
4. Create one client factory per trust boundary and reject missing configuration without echoing values.
5. Verify browser search with a read-only query and backend writes only against a disposable index.
6. Scan built assets and source history for accidental write-key exposure.

## Approval Boundaries

Do not install dependencies, create provider keys, alter secret stores, or rotate existing credentials outside the repository and account scope provided.

## Output

Return the dependency diff, client factories, environment-name contract, key/ACL matrix, verification results, secret-scan evidence, and remaining setup actions.

## Error Handling

| Condition | Response |
|---|---|
| v4 API appears in code | Use the official v5 migration guide before mixing patterns. |
| Key rejected | Verify application pairing, ACL, restriction, and environment. |
| Write key enters browser build | Stop, remove it, and rotate if exposed. |
| No safe test index | Limit verification to read-only search. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
runtime=node; package-manager=pnpm; client-major=5; browser=search-only
```

Expected handoff:

```text
read-check=pass; write-check=disposable-index-only; exposed-write-key=none
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [JavaScript API client](https://www.algolia.com/doc/libraries/javascript)
- [JavaScript v5 upgrade](https://www.algolia.com/doc/libraries/sdk/upgrade/javascript)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
