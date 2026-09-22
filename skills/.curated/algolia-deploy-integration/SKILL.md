---
name: algolia-deploy-integration
description: >-
  Plan and verify deployment of an Algolia-backed application with separated browser and server credentials. Use when releasing search code, index configuration, or event instrumentation. Trigger with "deploy Algolia", "Algolia production rollout", or "search release checklist".
argument-hint: "[repository-path] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- deployment
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Deployment Integration

## Overview

This skill coordinates application deployment with the Algolia assets it depends on. It treats code, records, settings, keys, and events as separate release surfaces with explicit ordering and rollback.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- The browser receives only a search-only or secured key; write-capable keys stay in trusted server or job environments.
- Pin application and index names per environment rather than deriving production targets from branch names.
- Complete indexing tasks and representative queries before routing production traffic.
- Deploy event instrumentation only after user-token, consent, query ID, and validation behavior are reviewed.

## Authentication

Provision custom least-privilege keys through the approved secret store. Never place Admin keys in static build variables, client bundles, deployment logs, or preview environments.

## Instructions

1. Map the deploy platform, runtime boundaries, environment variables, index targets, and current rollback mechanism.
2. Verify client packages and API usage against the pinned lockfile and current first-party docs.
3. Prepare or verify target records, settings, synonyms, and rules before the application cutover.
4. Deploy server and browser configuration with credential separation and redacted logging.
5. Run a read-only health check plus representative search tests against the intended target.
6. Record release SHA, index state, task receipts, smoke results, and rollback trigger.

## Approval Boundaries

Do not overwrite production indices, rotate keys, promote settings, or enable events as an implicit side effect of application deployment.

## Output

Return the release topology, environment map, credential classification, ordered deployment plan, smoke evidence, rollback steps, and unresolved approvals.

## Error Handling

| Condition | Response |
|---|---|
| Browser bundle contains write key | Stop deployment and rotate the exposed credential. |
| Target index is stale | Hold traffic and complete or rollback indexing. |
| Health check passes but relevance fails | Use representative query gates, not connectivity alone. |
| Rollback target unknown | Do not cut over. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
release=abc123; environment=production; browser-key=search-only; server-key=custom-write
```

Expected handoff:

```text
index-task=complete; smoke=pass; representative-queries=pass; rollback=previous-release
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
- [JavaScript API client](https://www.algolia.com/doc/libraries/javascript)
- [Sending events](https://www.algolia.com/doc/guides/sending-events)
