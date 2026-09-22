---
name: algolia-webhooks-events
description: >-
  Implement and validate Algolia click, conversion, and view events while separating them from source-to-index synchronization. Use when adding Insights, query attribution, or event-driven record updates. Trigger with "Algolia Insights", "track search conversion", or "sync database to Algolia".
argument-hint: "[repository-path] [event-or-sync-flow]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- events
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Search Events and Source Sync

## Overview

This skill corrects a common category error: user interaction events go to the Insights API, while database or business events drive an application-owned indexing pipeline. These flows have different identity, delivery, privacy, and retry contracts.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Use the dedicated `search-insights` client or supported framework integration for browser events; it is not the Search API client.
- Set `clickAnalytics` when a search-related event needs a returned query ID.
- Use a stable pseudonymous user token and preserve query ID, object IDs, positions, and event names as required.
- Design source-to-index updates as idempotent writes with ordering, dead-letter, replay, and reconciliation.

## Authentication

Browser events use the documented Insights credential pattern and must not contain write-capable keys or personal identifiers. Index sync uses a separate restricted backend key.

## Instructions

1. Classify the requested flow as user interaction telemetry, source-data synchronization, or both.
2. Map consent, user identity, query ID, object IDs, event taxonomy, and downstream feature consumers.
3. Implement events with the pinned `search-insights` or framework API and validate payloads using provider tooling.
4. Implement source sync separately with stable IDs, idempotency, bounded retry, dead-letter handling, and task waits.
5. Test missing query ID, duplicate delivery, consent denial, offline clients, reordered source events, and replay.
6. Measure event validity and index reconciliation, then document ownership and rollback.

## Approval Boundaries

Do not send personal identifiers as user tokens, invent attribution when query IDs are absent, or treat interaction events as database webhooks.

## Output

Return the flow classification, event and sync contracts, credential boundaries, validation results, retry and replay behavior, privacy decisions, and operational ownership.

## Error Handling

| Condition | Response |
|---|---|
| Query ID missing | Send only an appropriate non-search event or fix search attribution. |
| Consent denied | Do not emit the event. |
| Duplicate source event | Use idempotent version or event identity handling. |
| Validation rejects payload | Correct the contract before enabling downstream features. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
flow=search-clicks+catalog-updates; client=search-insights-2.17.3; consent=required
```

Expected handoff:

```text
events=validated; queryID-coverage=measured; sync=idempotent; dead-letter=tested
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Click and conversion events](https://www.algolia.com/doc/guides/sending-events)
- [Send events](https://www.algolia.com/doc/libraries/search-insights/send-events)
- [JavaScript API client](https://www.algolia.com/doc/libraries/javascript)
