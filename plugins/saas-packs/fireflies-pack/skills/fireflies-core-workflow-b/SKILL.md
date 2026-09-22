---
name: fireflies-core-workflow-b
description: >-
  Analyze authorized Fireflies meetings with current transcript filters and use AskFred only under explicit AI-credit, privacy, and citation controls. Use when performing scoped discovery or meeting Q&A. Trigger with "search Fireflies meetings", "AskFred analysis", or "query meetings for a topic".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <approved-query>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, search, askfred]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Search and AskFred Analysis

## Overview

Keep deterministic transcript discovery separate from generative AskFred analysis. Search results identify candidate records; an AI answer is derived output and must retain meeting provenance.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

transcripts supports keyword with scope TITLE, SENTENCES, or ALL, ISO-8601 fromDate/toDate, limit up to 50, skip pagination, mine, organizers, participants, and channel_id. title, organizer_email, and participant_email filters are deprecated. AskFred create/continue mutations consume AI credits.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Define an authorized cohort, time range, keyword, scope, and maximum result count.
2. Use current non-deprecated filters and page with limit and skip while enforcing a hard cap.
3. Select only IDs and low-sensitivity metadata during discovery.
4. Obtain approval and an AI-credit budget before creating an AskFred thread.
5. Bind meeting IDs or reviewed filters, ask a narrow question, and preserve thread and source identifiers.
6. Label answers as derived, validate material claims against accessible transcript evidence, and handle follow-ups in the same thread only when appropriate.
7. Record request counts, AI-credit outcome, provenance, and retention disposition.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before sentence-scope search, multi-meeting analysis, creating an AskFred thread, consuming AI credits, or retaining generated answers.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- require_ai_credits: stop and report the budget requirement; do not retry.
- Deprecated filter rejected: migrate to keyword, organizers, or participants.
- More than 50 requested: paginate within the approved cap.

## Examples

- "Find approved project reviews this month" uses keyword, TITLE scope, dates, and a cap.
- "Ask Fred across the whole company" is blocked pending cohort and credit approval.

## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
