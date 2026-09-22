---
name: algolia-core-workflow-b
description: >-
  Build a reliable Algolia indexing pipeline for full replacements, incremental updates, settings, synonyms, and rules. Use when a source of truth must publish deterministic search state. Trigger with "Algolia indexing workflow", "replace index records", or "sync Algolia".
argument-hint: "[repository-path] [source-dataset] [index-name]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- indexing
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Indexing Contract

## Overview

This skill designs the write path from an authoritative dataset to Algolia. It separates record transformation, validation, transport, task completion, and publication so a failed run cannot silently leave ambiguous search state.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Generate stable `objectID` values from source identities and reject duplicates before upload.
- Choose `saveObjects` for bounded upserts and `replaceAllObjects` only for an intentional full-state replacement.
- Wait for returned task IDs before verification or traffic cutover.
- Version settings, synonyms, and rules as reviewable inputs; do not infer them from production state during deployment.

## Authentication

Run indexing only from a trusted backend with a custom key restricted to the target indices and required write ACLs. Keep search-only keys out of indexing jobs.

## Instructions

1. Identify the source of truth, deletion semantics, index aliases or replicas, and acceptable publication window.
2. Transform and validate records locally, including size, required fields, stable IDs, and prohibited data.
3. Select incremental or full replacement based on source deletion guarantees and rollback needs.
4. Submit bounded batches, retain task IDs, and wait for completion with an overall timeout.
5. Verify counts, sentinel records, settings hashes, and representative queries.
6. Record the source snapshot, target index, completed tasks, and rollback or prior-index path.

## Approval Boundaries

Do not run a full replacement, delete records, change settings, or swap a production target until the source snapshot and rollback plan are approved.

## Output

Return the data contract, operation choice, validation report, task receipts, post-write checks, deletion behavior, and rollback instructions.

## Error Handling

| Condition | Response |
|---|---|
| Duplicate objectID | Fail before upload and report source records. |
| Partial batch failure | Stop publication and preserve successful task IDs. |
| Task timeout | Do not assume failure or success; query task state. |
| Verification mismatch | Keep the prior production target and investigate. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
source=snapshot-2026-09-10; mode=full-replacement; target=products_next
```

Expected handoff:

```text
records=48012; tasks=49-complete; sentinel-query=pass; cutover=pending-approval
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [JavaScript API client](https://www.algolia.com/doc/libraries/javascript)
- [Indexing guidance](https://www.algolia.com/doc/guides/sending-and-managing-data)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
