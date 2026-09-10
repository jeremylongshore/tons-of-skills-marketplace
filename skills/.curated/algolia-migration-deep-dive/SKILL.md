---
name: algolia-migration-deep-dive
description: >-
  Plan and execute a reversible migration from another search system or legacy index design to Algolia. Use when translating schemas, queries, relevance behavior, or production traffic. Trigger with "migrate to Algolia", "Algolia cutover", or "search engine migration".
argument-hint: "[repository-path] [source-system] [target-index]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- migration
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Search Migration

## Overview

This skill treats migration as a measured compatibility program: source data, query semantics, ranking, filters, UI behavior, traffic, and rollback are assessed separately before cutover.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Preserve the source system as the rollback authority until acceptance criteria pass.
- Translate capabilities from observed queries and product journeys, not feature-name similarity.
- Build a new target index and avoid in-place destructive conversion.
- Compare relevance with a representative, owner-approved query set and explicit tolerances.

## Authentication

Use separate least-privilege credentials for source reads, Algolia writes, and browser search. Keep all secret material outside migration artifacts.

## Instructions

1. Inventory source schema, analyzers, queries, filters, facets, ranking behavior, traffic, and operational constraints.
2. Define the Algolia record model, stable IDs, settings, synonyms, rules, and unsupported semantic gaps.
3. Backfill a new target index from a reproducible source snapshot and retain task receipts.
4. Run structural checks, representative query comparisons, latency observations, and UI acceptance tests.
5. Shadow or canary traffic when available, with named rollback thresholds and owners.
6. Cut over only after approval, then reconcile drift and retain the rollback window.

## Approval Boundaries

Do not overwrite the current production index, declare relevance equivalence from a few queries, or retire the source system before rollback expiry.

## Output

Return the capability map, data transform, gap register, backfill evidence, query comparison, cutover plan, acceptance decision, and rollback procedure.

## Error Handling

| Condition | Response |
|---|---|
| Unsupported query feature | Document the gap and design an approved product alternative. |
| Record counts differ | Reconcile filtering, deletes, and source snapshot boundaries. |
| Relevance regresses | Keep source traffic and tune against the approved query set. |
| Rollback data drifts | Define dual-write or replay before cutover. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
source=legacy-search; snapshot=snap-184; target=products_algolia_next
```

Expected handoff:

```text
records=reconciled; query-suite=198/200; two-gaps=owner-review; cutover=not-started
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Sending and managing data](https://www.algolia.com/doc/guides/sending-and-managing-data)
- [Relevance](https://www.algolia.com/doc/guides/managing-results)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
