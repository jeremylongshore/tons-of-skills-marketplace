---
name: algolia-reference-architecture
description: >-
  Design or review an Algolia search architecture across source data, indexing, query, UI, events, and operations. Use when establishing system boundaries or evaluating an existing integration. Trigger with "Algolia architecture", "design search platform", or "review Algolia integration".
argument-hint: "[repository-path] [system-scope]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- architecture
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Reference Architecture

## Overview

This skill produces an evidence-backed architecture tailored to the repository. It avoids presenting optional Algolia products or provider features as mandatory and makes trust, data, and failure boundaries explicit.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- The source system remains authoritative; Algolia is a derived search projection.
- Separate indexing, browser search, server search, events, analytics, and workforce administration trust zones.
- Version record transforms and search configuration with the application.
- Design task completion, reconciliation, observability, and rollback before production cutover.

## Authentication

Assign distinct least-privilege credentials to each machine actor and use provider team controls for human access. Generate tenant-scoped secured keys only on trusted servers.

## Instructions

1. Map current components, data stores, producers, consumers, credentials, indices, and deployment environments.
2. Define the record contract, stable identity, deletion semantics, settings ownership, and freshness objective.
3. Choose query and UI boundaries, including browser versus server execution and tenant restrictions.
4. Add event flow only where consent, user-token, query-ID, and validation requirements are owned.
5. Model failures for source lag, partial indexing, key denial, provider degradation, and relevance regressions.
6. Produce architecture decisions, interfaces, tests, observability, rollout, and rollback.

## Approval Boundaries

Do not select paid features, centralize unrestricted credentials, or authorize a migration solely from a generic reference diagram.

## Output

Return the as-is and proposed boundaries, data and trust flows, decision records, interfaces, failure modes, security controls, validation plan, and phased rollout.

## Error Handling

| Condition | Response |
|---|---|
| Repository contradicts assumed topology | Follow repository evidence and revise the design. |
| Feature entitlement unknown | Mark it optional pending current account confirmation. |
| Trust boundary crosses browser | Replace write access with a backend capability. |
| Rollback projection missing | Add a retained prior target or rebuild path. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
scope=catalog-search; source=postgres; consumers=web,mobile; tenants=120
```

Expected handoff:

```text
projection=versioned; browser=secured-search; indexing=job-key; rollback=prior-index
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Sending and managing data](https://www.algolia.com/doc/guides/sending-and-managing-data)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
- [Sending events](https://www.algolia.com/doc/guides/sending-events)
