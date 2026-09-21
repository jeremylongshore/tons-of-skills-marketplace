---
name: fireflies-upgrade-migration
description: >-
  Migrate Fireflies GraphQL documents and webhook consumers away from deprecated fields and legacy event shapes with dual-read evidence and rollback. Use when responding after schema drift or documentation changes. Trigger with "upgrade Fireflies API", "Fireflies deprecated field", or "migrate Fireflies webhook".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, migration, graphql]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Schema and Contract Migration

## Overview

Migrate Fireflies GraphQL documents and webhook consumers away from deprecated fields and legacy event shapes with dual-read evidence and rollback.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

Current transcript-list filters replace title with keyword and replace organizer_email and participant_email with organizers and participants. Webhooks V2 uses event, timestamp, meeting_id, and granular meeting.transcribed or meeting.summarized events instead of the V1 eventType shape.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Inventory static GraphQL documents, selected fields, response parsers, webhook payloads, and fixtures.
2. Map deprecated fields and V1 webhook assumptions to current documented contracts.
3. Add compatibility parsing only where a measured transition requires it.
4. Update synthetic fixtures and contract tests before production traffic.
5. Run shadow comparisons on authorized metadata and compare IDs, counts, nullability, and event sequencing.
6. Cut over one operation or event family at a time with rollback flags.
7. Remove compatibility code only after the observation window and owner sign-off.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before enabling a new event subscription, widening transcript search, changing selected sensitive fields, or removing rollback compatibility.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- New field is absent: preserve nullability and verify entitlement or processing state.
- Duplicate V1/V2 events: deduplicate on event identity and meeting ID.
- Result-set drift: halt cutover and compare filter semantics.

## Examples

- "Review fireflies schema and contract migration" produces a bounded plan and redacted receipt.
- A request that widens access or mutates production is paused at the approval boundary.

## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
