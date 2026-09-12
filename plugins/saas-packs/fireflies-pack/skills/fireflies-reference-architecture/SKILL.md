---
name: fireflies-reference-architecture
description: >-
  Design a Fireflies architecture that separates identity, GraphQL reads, privileged mutations, Webhooks V2 intake, queues, sensitive data, and derived outputs. Use when performing system design or review. Trigger with "Fireflies architecture", "design Fireflies pipeline", or "Fireflies integration blueprint".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, architecture, governance]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Governed Integration Architecture

## Overview

Design a Fireflies architecture that separates identity, GraphQL reads, privileged mutations, Webhooks V2 intake, queues, sensitive data, and derived outputs.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

Use separate trust boundaries for bearer-authenticated outbound GraphQL, signature-authenticated inbound events, durable orchestration, meeting-content storage, and derived destinations. An event carries an identity, not permission to fetch every field.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Map actors, principals, environments, operations, event types, data classes, and sinks.
2. Keep API and signing secrets in separate managed stores and rotation paths.
3. Place static GraphQL documents behind a policy-aware service boundary.
4. Verify and acknowledge webhooks at the edge, then enqueue idempotent jobs.
5. Fetch only authorized fields and isolate raw, summarized, and derived data stores.
6. Add per-operation budgets, audit receipts, dead letters, deletion propagation, and rollback controls.
7. Threat-model cross-team access, replay, duplicate events, stale processing, and downstream leakage.


## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before adding a new data sink, privileged mutation, team-wide event scope, long-term content store, or cross-tenant processing path.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- Event arrives without fetch authority: acknowledge or quarantine without retrieving content.
- Downstream write fails: retry idempotently within retention and budget policy.
- Deletion request cannot propagate: stop new processing and escalate governance ownership.

## Examples

- "Review fireflies governed integration architecture" produces a bounded plan and redacted receipt.
- A request that widens access or mutates production is paused at the approval boundary.


## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
