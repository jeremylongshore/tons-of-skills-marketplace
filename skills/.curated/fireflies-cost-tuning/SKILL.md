---
name: fireflies-cost-tuning
description: >-
  Control Fireflies request quotas, AskFred AI credits, recording volume, storage, and seat utilization without deleting transcripts or changing plans automatically. Use when performing spend review or budget enforcement. Trigger with "Fireflies cost", "AskFred credits", or "right-size Fireflies".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, cost, governance]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Quota and AI-Credit Control

## Overview

Control Fireflies request quotas, AskFred AI credits, recording volume, storage, and seat utilization without deleting transcripts or changing plans automatically.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

Costs span subscription seats, recorded volume, storage or retention, API request budgets, and AskFred AI credits. API observations can inform decisions but do not authorize plan, recording, retention, role, or deletion changes.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Define the billing period, team, approved metrics, and accountable owner.
2. Measure request counts by operation and AskFred success or require_ai_credits outcomes.
3. Use approved user metadata to identify candidate seat utilization without exposing meetings.
4. Separate unnecessary polling and oversized selections from legitimate workload.
5. Model savings from batching, event-driven processing, field minimization, and policy changes.
6. Present reversible recommendations with confidence and operational impact.
7. Track approved actions and validate savings without deleting records as a test.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before plan or seat changes, recording-policy changes, retention changes, AskFred use, bulk export, or transcript deletion.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- Usage data incomplete: state the gap and avoid projected certainty.
- require_ai_credits: do not purchase or retry automatically.
- Deletion proposed for savings: require retention, legal, and owner review.

## Examples

- "Review fireflies quota and ai-credit control" produces a bounded plan and redacted receipt.
- A request that widens access or mutates production is paused at the approval boundary.

## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
