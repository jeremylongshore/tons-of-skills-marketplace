---
name: fireflies-security-basics
description: >-
  Harden Fireflies bearer authentication, GraphQL selections, webhook signatures, logs, and privileged mutations against secret and meeting-data exposure. Use when performing security review or baseline implementation. Trigger with "secure Fireflies", "Fireflies threat model", or "Fireflies key safety".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, security, webhooks]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Integration Security Baseline

## Overview

Harden Fireflies bearer authentication, GraphQL selections, webhook signatures, logs, and privileged mutations against secret and meeting-data exposure.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

Protect two independent secrets: the API bearer key for outbound GraphQL and the Webhooks V2 signing secret for inbound HMAC verification. Verify X-Hub-Signature over the raw body as sha256=HEX_DIGEST with a timing-safe comparison before parsing.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Inventory API keys, webhook secrets, principals, environments, and data flows.
2. Keep bearer calls server-side and use separate secrets per environment.
3. Restrict GraphQL documents and selected fields to reviewed operations.
4. Verify webhook signatures on raw bytes, reject missing or malformed headers, then parse JSON.
5. Redact Authorization, signatures, meeting IDs, emails, text, summaries, and media URLs from logs.
6. Gate role, privacy, sharing, channel, upload, live-meeting, and deletion mutations.
7. Test key rotation, replay handling, redaction, and incident response.


## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before any production key or signing-secret change, privacy/share mutation, role change, recording/upload, or transcript deletion.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- Signature mismatch: return 401 and preserve only safe delivery metadata.
- Suspected bearer leak: revoke or rotate through the incident owner and audit access.
- Unreviewed field selection: block deployment until data classification is complete.

## Examples

- "Review fireflies integration security baseline" produces a bounded plan and redacted receipt.
- A request that widens access or mutates production is paused at the approval boundary.


## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
