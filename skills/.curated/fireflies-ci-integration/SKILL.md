---
name: fireflies-ci-integration
description: >-
  Build a Fireflies CI lane with static GraphQL validation, synthetic fixtures, secret scanning, webhook vectors, and narrowly gated live tests. Use when adding automated verification. Trigger with "Fireflies CI", "test Fireflies GraphQL", or "Fireflies contract test".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, ci, testing]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Contract-Safe CI

## Overview

Build a Fireflies CI lane with static GraphQL validation, synthetic fixtures, secret scanning, webhook vectors, and narrowly gated live tests.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

Most CI should be offline and deterministic. Live tests require an explicitly provisioned read-only test identity, selected metadata fields, strict budgets, and no production meeting data.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Collect named GraphQL documents and validate syntax and variable declarations offline.
2. Test success, partial data, errors, nulls, pagination, and throttling with synthetic fixtures.
3. Verify Webhooks V2 HMAC vectors against raw bytes, malformed signatures, and duplicate events.
4. Add secret and sensitive-output assertions for logs and artifacts.
5. Gate optional live tests behind protected secrets and an explicit environment approval.
6. Limit live queries to approved metadata and one bounded request budget.
7. Publish test counts and safe failure metadata, never response bodies.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before enabling live CI, adding a mutation test, storing a Fireflies key, or retaining any API response artifact.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- No test key: skip the live lane without weakening offline gates.
- Live data appears in artifacts: stop publication and invoke incident handling.
- Schema validation fails: update documents from current first-party evidence.

## Examples

- "Review fireflies contract-safe ci" produces a bounded plan and redacted receipt.
- A request that widens access or mutates production is paused at the approval boundary.

## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
