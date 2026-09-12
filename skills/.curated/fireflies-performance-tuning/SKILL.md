---
name: fireflies-performance-tuning
description: >-
  Reduce Fireflies latency and quota use through field minimization, bounded pagination, caching of non-sensitive metadata, and asynchronous webhook-driven retrieval. Use when calls are slow or wasteful. Trigger with "speed up Fireflies", "optimize Fireflies query", or "reduce Fireflies calls".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, performance, graphql]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies GraphQL Performance Tuning

## Overview

Reduce Fireflies latency and quota use through field minimization, bounded pagination, caching of non-sensitive metadata, and asynchronous webhook-driven retrieval.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

GraphQL performance starts with smaller field selections and fewer calls. transcripts pages at most 50 records; cache only approved metadata, never assume summaries or sentences are immutable while processing, and prefer Webhooks V2 over aggressive polling.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Measure latency, response bytes, selected fields, pages, errors, and quota use by operation.
2. Remove unused nested fields and split metadata discovery from sensitive detail retrieval.
3. Set explicit result caps and page only while the caller still needs data.
4. Replace processing-status polling with meeting.transcribed or meeting.summarized events where appropriate.
5. Cache only classified metadata with tenant-aware keys and bounded TTLs.
6. Limit concurrency below the applicable plan and operation budgets.
7. Compare before/after metrics on synthetic or approved records and keep rollback settings.


## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before caching meeting-derived data, increasing concurrency, widening selections, or using a broader transcript cohort.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- Faster query returns less required data: reject the optimization.
- Cache crosses principals or tenants: purge through the approved incident procedure.
- Polling causes throttling: stop and switch to event-driven status where supported.

## Examples

- "Review fireflies graphql performance tuning" produces a bounded plan and redacted receipt.
- A request that widens access or mutates production is paused at the approval boundary.


## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
