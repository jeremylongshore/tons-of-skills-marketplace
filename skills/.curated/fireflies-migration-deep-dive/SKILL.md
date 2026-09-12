---
name: fireflies-migration-deep-dive
description: >-
  Migrate authorized recordings into Fireflies through current uploadAudio or addToLiveMeeting contracts with provenance, consent, limits, callbacks, and rollback planning. Use when performing import or live-meeting onboarding. Trigger with "upload audio to Fireflies", "import recordings", or "add Fireflies to live meeting".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, ingestion, migration]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Governed Audio Ingestion

## Overview

Migrate authorized recordings into Fireflies through current uploadAudio or addToLiveMeeting contracts with provenance, consent, limits, callbacks, and rollback planning.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

uploadAudio accepts a publicly downloadable HTTPS media URL and documented mp3, mp4, wav, m4a, or ogg formats; current size limits differ for audio, free-tier video, and paid-tier video. addToLiveMeeting accepts supported meeting links and is limited to 3 requests per 20 minutes.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Inventory source recordings, ownership, consent, format, size, retention, and destination team.
2. Reject preview links, expiring links that cannot survive ingestion, and unauthorized public exposure.
3. Choose uploadAudio for recordings or addToLiveMeeting for an approved supported live meeting.
4. Attach a non-sensitive client reference and approved callback only when needed.
5. Submit a small canary, record the returned status without logging the source URL, and wait for current webhook events.
6. Validate transcript identity, expected duration, processing status, and authorized metadata before scaling.
7. Batch within quotas, track provenance, remove temporary public access, and reconcile failures.


## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before exposing a media URL, uploading real recordings, adding a bot to a live meeting, configuring callbacks, or scaling a batch.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- Media URL is not public HTTPS or downloadable: do not weaken storage controls blindly.
- unsupported_platform or invalid language: correct reviewed input instead of retrying.
- Timeout after submission: reconcile by client reference or webhook before resubmitting.

## Examples

- "Review fireflies governed audio ingestion" produces a bounded plan and redacted receipt.
- A request that widens access or mutates production is paused at the approval boundary.


## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
