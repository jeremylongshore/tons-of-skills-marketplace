---
name: fireflies-webhooks-events
description: >-
  Implement a current Fireflies Webhooks V2 consumer with raw-body HMAC verification, event allowlisting, idempotency, ordering tolerance, and fast acknowledgement. Use when performing meeting lifecycle automation. Trigger with "Fireflies webhook v2", "meeting.transcribed event", or "verify Fireflies signature".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, webhooks, events]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Webhooks V2 Consumer

## Overview

Implement a current Fireflies Webhooks V2 consumer with raw-body HMAC verification, event allowlisting, idempotency, ordering tolerance, and fast acknowledgement.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

V2 payloads contain event, timestamp, meeting_id, and optional client_reference_id. Documented events include meeting.transcribed and meeting.summarized. X-Hub-Signature is sha256=<hex HMAC> over the raw body; valid deliveries need a 2xx response within 10 seconds.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Subscribe only to approved V2 event types at an HTTPS endpoint.
2. Capture raw bytes and validate the signature format and timing-safe HMAC before JSON parsing.
3. Validate event, timestamp, meeting_id, and optional client reference against a strict schema.
4. Reject unknown events or route them to a quarantined metadata-only lane.
5. Deduplicate using delivery metadata plus event and meeting identity, and tolerate summarized arriving after transcribed.
6. Acknowledge quickly, then fetch authorized data asynchronously if needed.
7. Record signature result, event type, latency, dedupe outcome, and job ID without payload content.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before subscribing to team-wide events, fetching transcript content after an event, replaying a delivery, or retaining payloads.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- Missing signature when verification is configured: return 401.
- Duplicate delivery: acknowledge without repeating side effects.
- Unknown event: quarantine metadata and do not infer a schema.

## Examples

- "Review fireflies webhooks v2 consumer" produces a bounded plan and redacted receipt.
- A request that widens access or mutates production is paused at the approval boundary.

## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
