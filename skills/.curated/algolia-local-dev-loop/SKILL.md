---
name: algolia-local-dev-loop
description: >-
  Create a fast local development loop for Algolia record transforms and search behavior without contaminating shared indices. Use when iterating on search code, fixtures, or client wrappers. Trigger with "Algolia local development", "mock Algolia", or "test search locally".
argument-hint: "[repository-path] [test-mode]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- development
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Local Development Loop

## Overview

This skill combines deterministic offline tests with an optional disposable-index integration test. It makes the local loop useful without pretending a mock reproduces provider ranking, task timing, or authorization.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Keep record transformation and query construction in pure functions that can be tested offline.
- Mock only the application-owned client boundary, not internal SDK implementation details.
- Use unique disposable index names for live checks and never reuse production credentials.
- Wait for write tasks and clean up live fixtures explicitly.

## Authentication

Offline tests need no credential. Optional live tests use a custom key restricted to the disposable prefix and are disabled when credentials are absent.

## Instructions

1. Inspect the current client wrapper, package scripts, fixtures, and test framework.
2. Extract pure record-shaping and query-building functions with focused unit tests.
3. Create a typed adapter and mock its application-level responses and failures.
4. Add an opt-in live test that validates a generated disposable index name.
5. Write known records, wait, query, assert, and clean up while retaining task receipts.
6. Document how developers select offline versus live mode and how stale test indices are reported.

## Approval Boundaries

Do not require live credentials for the default test command, share a personal Admin key, or clean up any index outside the validated disposable prefix.

## Output

Return the local scripts, test boundary, fixtures, live-test guard, cleanup behavior, and evidence for both credential-free and optional integration modes.

## Error Handling

| Condition | Response |
|---|---|
| Credential absent | Run offline tests and report the live test as skipped. |
| Mock diverges from adapter | Update the adapter contract and its typed fixture together. |
| Disposable prefix invalid | Fail before any network write. |
| Cleanup fails | Report the exact retained index for manual review. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
mode=offline-default; integration=ALGOLIA_LIVE_TEST=1; prefix=dev-$USER-$RUN
```

Expected handoff:

```text
unit=pass; live=skipped; production-index-access=none
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [JavaScript API client](https://www.algolia.com/doc/libraries/javascript)
- [JavaScript v5 upgrade](https://www.algolia.com/doc/libraries/sdk/upgrade/javascript)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
