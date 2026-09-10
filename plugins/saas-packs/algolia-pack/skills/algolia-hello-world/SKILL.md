---
name: algolia-hello-world
description: >-
  Create a minimal Algolia JavaScript v5 indexing and search proof using a disposable index. Use when verifying credentials, learning the client boundary, or proving first connectivity. Trigger with "Algolia hello world", "first Algolia search", or "test Algolia setup".
argument-hint: "[project-path] [disposable-index]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- getting-started
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Verified First Search

## Overview

This skill proves the smallest complete write-read-cleanup cycle: create known records, wait for the indexing task, query one record, and remove the disposable index after review.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Use the installed `algoliasearch` v5 client; methods such as `saveObjects`, `waitForTask`, and `searchSingleIndex` are called on the client.
- Assign explicit `objectID` values so verification is deterministic.
- Use a new disposable index, never an existing production index.
- Treat cleanup as an observed task with its own result.

## Authentication

Use a custom backend key restricted to the disposable index and necessary operations. The browser should never receive this write credential.

## Instructions

1. Confirm the package version, application ID, credential source, and validated disposable index name.
2. Create two non-sensitive records with stable object IDs.
3. Save the records and retain the returned task ID.
4. Wait for that task, then search for one unique value with `searchSingleIndex`.
5. Assert the expected object ID and record the request metadata without secrets.
6. After human confirmation, delete the disposable index and verify cleanup.

## Approval Boundaries

Do not use a production index, copy an Admin key into source, or delete an index until its exact disposable name is displayed and approved.

## Output

Return package and API evidence, the redacted configuration, write and wait task IDs, search assertion, cleanup result, and next recommended integration step.

## Error Handling

| Condition | Response |
|---|---|
| Authentication fails | Verify application/key pairing and required ACL. |
| Search is empty after write | Wait for the recorded task and confirm index name. |
| Unexpected existing records | Stop; the index is not disposable. |
| Cleanup not approved | Leave the index and report its exact name. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
app=APP…9X; index=skill-smoke-20260910; records=2
```

Expected handoff:

```text
save-task=complete; expected-object=movie-1; search=pass; cleanup=approved-and-complete
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [JavaScript API client](https://www.algolia.com/doc/libraries/javascript)
- [JavaScript v5 upgrade](https://www.algolia.com/doc/libraries/sdk/upgrade/javascript)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
