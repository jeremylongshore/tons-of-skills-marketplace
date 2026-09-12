---
name: assemblyai-webhooks-events
description: >-
  Analyze and process AssemblyAI pre-recorded and streaming webhooks with authentication, fast acknowledgment, deduplication, and safe retrieval. Use when implementing event-driven completion. Trigger with "AssemblyAI webhook" or "AssemblyAI callback".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<callback-route> <event-family>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, assemblyai]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live AssemblyAI work requires network access"
---
# AssemblyAI Authenticated Webhook Processing

## Overview

Process callbacks as authenticated, repeatable delivery attempts. Keep acknowledgment, content retrieval, persistence, replay, credentials, and deletion separately governed.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The AssemblyAI project, environment, region, data classification, and accountable owner.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Pre-recorded callbacks carry transcript ID and status; fetch the full transcript separately. Streaming callbacks after termination can carry finalized turns. AssemblyAI documents a 10-second acknowledgment window and up to 10 attempts when no 2xx is received; a 4xx stops retries. Verify the configured custom auth header.

## Authentication

For live work, inject `ASSEMBLYAI_API_KEY` from an approved secret manager and send the raw value only in the AssemblyAI `Authorization` header to the configured first-party host. Never print, commit, place in a URL, or expose it to an untrusted client. Callback secrets and temporary streaming tokens are separate credentials.

## Instructions

1. Bind each route to the correct event schema.
2. Capture bounded raw bytes and verify the auth header before parsing.
3. Validate content type and allowlisted fields.
4. Derive a durable dedupe key from family and stable identity.
5. Persist approved minimized data, then return 2xx within deadline.
6. Retrieve pre-recorded results by ID and quarantine schema drift.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call AssemblyAI, upload audio, open a streaming session, mint a token, replay a callback, deploy, rotate a key, or delete a transcript merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live audio processing, production credential or endpoint changes, paid model or capacity changes, content retention, callback replay, deployment, or deletion. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- A transient 4xx can cause permanent loss because retries stop.
- IP allowlisting supplements but does not replace callback auth.
- Duplicate delivery must not duplicate downstream actions.

## Output

Return the operation scope, environment, region, contract surface, authorization class, model and feature decisions, deterministic validation results, content-free identifiers, risks, cleanup or rollback state, and a concise pass/fail receipt. Exclude credentials, signed URLs, audio, transcript text, prompts, and customer-derived content.

## Example

- Start with the named environment, approved regional host, synthetic fixture identity, and bounded operation budget.
- Finish with safe IDs, contract and assertion counts, terminal state, cleanup status, and the decision owner; never reproduce speech content.

## Validation

Rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm rollback, termination, or deletion state before reporting success.

## References

Review the dated first-party evidence map before relying on any model, parameter, limit, price, region, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
