---
name: algolia-incident-runbook
description: >-
  Diagnose and manage an Algolia-backed search incident with evidence, containment, and reversible recovery. Use when users see failed, stale, slow, or irrelevant search results. Trigger with "Algolia incident", "search outage", or "Algolia degraded".
argument-hint: "[repository-path] [incident-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- incident-response
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Search Incident Runbook

## Overview

This skill runs a product-owned incident process without assuming the provider is or is not at fault. Severity and response targets come from the organization's runbook, while diagnosis uses application, provider, and data-pipeline evidence.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Separate availability, authorization, freshness, latency, relevance, and event-collection symptoms.
- Check provider status as one signal, not as the root-cause conclusion.
- Preserve request IDs, task IDs, deployment SHAs, settings changes, and source snapshots.
- Prefer traffic rollback, prior index targets, or feature degradation paths that are already tested.

## Authentication

Use read-only or narrowly scoped incident credentials. Never paste keys into tickets, chat, commands, screenshots, or diagnostic bundles.

## Instructions

1. Declare incident owner, affected journey, start time, severity source, and current user impact.
2. Freeze unrelated changes and capture recent releases, indexing runs, key changes, and provider status.
3. Run a known read-only query and compare application, direct client, and source-of-truth results.
4. Classify the failure surface and choose the smallest reversible containment.
5. Verify recovery with synthetic and representative user queries, not only HTTP success.
6. Record timeline, evidence, decisions, cleanup, follow-up owners, and rollback readiness.

## Approval Boundaries

Do not invent severity targets, rotate credentials, rebuild production, change relevance settings, or delete an index without the incident commander's approval.

## Output

Return the incident classification, timeline, evidence links, containment action, recovery checks, customer impact, unresolved risks, and follow-up tasks.

## Error Handling

| Condition | Response |
|---|---|
| Provider status unclear | Continue application and data-path diagnosis while monitoring official status. |
| Credential suspected exposed | Escalate rotation through the approved secret process. |
| Freshness mismatch | Trace source snapshot and task completion before reindexing. |
| Recovery changes relevance | Rollback or obtain product-owner acceptance. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
incident=SEV-from-company-runbook; symptom=stale-products; provider-status=operational
```

Expected handoff:

```text
cause=indexing-task-failed; containment=previous-index; verification=12/12-queries-pass
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Algolia status](https://status.algolia.com/)
- [Monitoring API](https://www.algolia.com/doc/rest-api/monitoring)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
