---
name: fireflies-local-dev-loop
description: >-
  Build a deterministic Fireflies development loop with recorded synthetic GraphQL fixtures, schema-contract tests, and no dependency on production meeting data. Use when implementing or debugging locally. Trigger with "Fireflies local development", "mock Fireflies GraphQL", or "Fireflies test fixture".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <test-command>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, development, testing]
model: inherit
effort: medium
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Privacy-Safe Local Development

## Overview

Make local work reproducible without copying real transcripts, participant lists, summaries, or bearer keys onto developer machines.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

Model GraphQL responses as data plus optional errors, preserve nullability, and keep separate fixtures for success, partial data, validation failure, authorization failure, rate limiting, and delayed processing.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Map the integration's operations and selected fields before creating fixtures.
2. Create synthetic meetings with invented IDs, speakers, sentences, summaries, and timestamps.
3. Record the exact GraphQL envelope shape, including errors and extensions where used.
4. Place the transport behind an injectable interface and route local tests to a deterministic mock server.
5. Add contract tests for null fields, pagination, partial data, and redaction.
6. Keep live tests opt-in, read-only, narrowly selected, and disabled without an explicit test key.
7. Document how fixtures are refreshed after a reviewed schema change.


## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before recording a live response, connecting a local process to production, or storing any real meeting-derived content.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- Fixture drift: update only from current schema evidence and review the diff.
- Secret appears in snapshot: stop, revoke if exposed, and remove it from history through the approved incident path.
- Mock-only success: run the authorized read-only contract lane before release.

## Examples

- "Mock a completed transcript" uses invented participant and sentence data.
- "Download one customer meeting for fixtures" is rejected.


## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
