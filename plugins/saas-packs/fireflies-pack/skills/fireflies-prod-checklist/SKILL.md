---
name: fireflies-prod-checklist
description: >-
  Run a fail-closed readiness review for a Fireflies integration covering identity, schema contracts, privacy, quotas, webhooks, observability, rollback, and ownership. Use when preparing before enabling production traffic. Trigger with "Fireflies production checklist", "ship Fireflies integration", or "Fireflies go-live review".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, production, governance]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Production Readiness Gate

## Overview

Run a fail-closed readiness review for a Fireflies integration covering identity, schema contracts, privacy, quotas, webhooks, observability, rollback, and ownership.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

Readiness is evidence, not a successful demo. The release must prove its exact operations, selected fields, permission model, quotas, webhook behavior, failure modes, rollback, and retention controls against the current public contract.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Pin the release revision and enumerate GraphQL operations and Webhooks V2 events.
2. Verify secret ownership, rotation, redaction, and environment isolation.
3. Review every selected field and derived output against classification and retention.
4. Exercise success, GraphQL error, timeout, throttling, null/processing, invalid signature, and duplicate webhook paths.
5. Confirm operation-specific budgets, queue limits, alerts, dashboards, and runbooks.
6. Test rollback or feature disablement without deleting source records.
7. Obtain accountable approvals and archive a content-free launch receipt.


## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before production enablement, elevated roles, broad meeting access, destructive mutations, or accepting an untested rollback.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- Any required evidence absent: fail the gate.
- Schema or docs changed after review: rerun affected checks.
- Rollback cannot stop writes or webhook processing: do not launch.

## Examples

- "Review fireflies production readiness gate" produces a bounded plan and redacted receipt.
- A request that widens access or mutates production is paused at the approval boundary.


## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
