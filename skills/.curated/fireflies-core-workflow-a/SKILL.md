---
name: fireflies-core-workflow-a
description: >-
  Analyze and retrieve an authorized Fireflies transcript with minimal fields, explicit ownership checks, pagination awareness, and safe handling of sentences and summaries. Use when integrating meeting records. Trigger with "fetch Fireflies transcript", "read meeting summary", or "Fireflies transcript fields".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <transcript-id>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, transcripts, privacy]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Transcript Retrieval Boundary

## Overview

Treat a transcript as sensitive meeting data. Separate metadata, summary, sentences, analytics, media links, attendance, and sharing fields so callers receive only what their use case permits.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

Use transcript(id: String!) for one record. Meeting ID and transcript ID refer to the same platform identity. Selected fields have different sensitivity and entitlement requirements; analytics requires an eligible plan, and is_live changes whether sentences are live captions or processed transcript data.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Confirm the requesting principal may access the target transcript and state the business purpose.
2. Classify each requested field and remove participants, sentences, media URLs, or analytics unless necessary.
3. Send a named transcript query with the ID as a variable.
4. Reject object_not_found as either absence or inaccessible data without probing other IDs.
5. Validate the returned ID, processing status, nullability, and expected organizer or ownership metadata.
6. Route content through the approved redaction and retention boundary before downstream use.
7. Return a receipt with selected field groups and record count, never the meeting body.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before retrieving sentences, raw_text, audio_url, video_url, participant identifiers, attendance, analytics, or externally shared access.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- object_not_found: do not enumerate adjacent IDs; verify authorization and the supplied ID.
- Summary is null: inspect processing state and wait rather than fabricating a result.
- is_live is true: do not treat captions as a finalized transcript.

## Examples

- "Read the title and summary status" requests only those fields.
- "Export every sentence to logs" is rejected.

## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
