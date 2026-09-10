---
name: algolia-sdk-patterns
description: >-
  Create or review a typed application adapter around the Algolia JavaScript v5 client. Use when client calls, index names, errors, task waits, and credential usage are scattered. Trigger with "Algolia SDK patterns", "Algolia client wrapper", or "refactor search client".
argument-hint: "[repository-path] [adapter-module]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- sdk
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia JavaScript v5 SDK Boundary

## Overview

This skill centralizes the application contract around the installed v5 client without hiding important provider results. It keeps search, writes, task waits, and error metadata testable and explicit.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Create clients at trust boundaries and inject them into adapters rather than constructing them in every call site.
- For v5, call operations on the client and pass `indexName`; do not restore `initIndex`.
- Return typed application results while preserving request IDs, task IDs, and provider error context.
- Put retry, timeout, batching, and index resolution policies in one reviewed layer.

## Authentication

Accept credentials from the approved runtime configuration and never expose them through adapter return values, exceptions, logs, or browser/server boundary mistakes.

## Instructions

1. Inventory every SDK import, installed version, client construction, index name, and direct call.
2. Group use cases into search, indexing, configuration, events, analytics, or administration boundaries.
3. Define typed inputs and outputs plus explicit timeout, task-wait, and error behavior.
4. Implement the smallest adapter and migrate one caller with contract tests.
5. Test success, authorization denial, timeout, stale task, malformed filters, and cancellation.
6. Migrate remaining callers incrementally and remove duplicate credential or retry logic.

## Approval Boundaries

Do not conceal destructive index operations behind generic methods, silently retry writes, or migrate all callers without a compatibility and rollback plan.

## Output

Return the call-site inventory, adapter API, trust boundaries, migrated callers, contract tests, preserved metadata, and remaining direct-client exceptions.

## Error Handling

| Condition | Response |
|---|---|
| Installed types differ from docs | Follow the lockfile and types; schedule version review separately. |
| Provider error is flattened | Preserve status and correlation metadata. |
| Task wait is omitted | Make completion semantics explicit in write results. |
| Adapter gains unrelated policy | Split the boundary by use case. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
module=src/search/algolia.ts; version=5.59.0; callers=14
```

Expected handoff:

```text
adapter=SearchGateway+IndexPublisher; migrated=3; contract-tests=pass; retries=centralized
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [JavaScript API client](https://www.algolia.com/doc/libraries/javascript)
- [JavaScript v5 upgrade](https://www.algolia.com/doc/libraries/sdk/upgrade/javascript)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
