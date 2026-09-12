---
name: fireflies-hello-world
description: >-
  Run the smallest current Fireflies GraphQL query and verify identity, response structure, and data-minimization controls without dumping transcripts. Use when testing a new server-side integration. Trigger with "Fireflies hello world", "first Fireflies query", or "verify Fireflies setup".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <environment>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, graphql, quickstart]
model: inherit
effort: low
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies First Metadata Query

## Overview

Prove the GraphQL transport with low-sensitivity metadata. Do not use a real meeting transcript as a quick-start fixture or log user email addresses merely to show that the request worked.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

The public API is GraphQL over POST. A minimal user or users selection is the documented quickstart; clients must examine the top-level errors array even when the HTTP response is 200 and request only fields necessary for the smoke test.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Confirm the API key owner and test environment are authorized for the request.
2. Choose the user query and select only an opaque identifier or other approved metadata.
3. Send one POST request with JSON query and variables from a server-side client.
4. Assert HTTP success, absence of GraphQL errors, presence of data, and the expected response shape.
5. Log only timing, operation name, correlation ID, and pass/fail status.
6. Exercise a synthetic failure without exposing the bearer key.
7. Keep the smoke test only if its data access and request budget are acceptable.


## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before selecting emails, integrations, transcripts, sentences, summaries, audio URLs, or any other meeting-derived field.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- Empty data: distinguish a valid empty result from an authorization or query error.
- GraphQL validation error: compare the selected fields with current docs or schema evidence.
- Rate limit: stop retries and honor the current plan and any retryAfter value.

## Examples

- "Verify the endpoint" selects only user_id and returns a content-free receipt.
- "Print my five latest meetings" is routed to an approved transcript workflow instead.


## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
