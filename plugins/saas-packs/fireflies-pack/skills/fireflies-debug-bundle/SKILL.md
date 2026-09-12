---
name: fireflies-debug-bundle
description: >-
  Assemble a content-free Fireflies diagnostic bundle covering identity, operation shape, limits, latency, processing state, and deployment configuration. Use when performing escalation without exposing meetings or secrets. Trigger with "Fireflies debug bundle", "collect Fireflies diagnostics", or "Fireflies support evidence".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, diagnostics, privacy]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Privacy-Safe Diagnostic Bundle

## Overview

Assemble a content-free Fireflies diagnostic bundle covering identity, operation shape, limits, latency, processing state, and deployment configuration.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

A support bundle should prove what happened without containing Authorization, query variables with identifiers, transcript text, summaries, participant data, media URLs, webhook bodies, or signing secrets.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Record repository revision, runtime, dependency versions, environment name, and operation name.
2. Capture redacted request shape and selected field names, not variable values.
3. Include HTTP status, GraphQL codes, retryAfter, timing, and correlation identifiers.
4. Summarize identity role and entitlement without emails or tokens.
5. Include webhook signature pass/fail and event type without the raw body when relevant.
6. Scan the bundle for bearer tokens, secrets, meeting text, URLs, and personal data.
7. Encrypt and retain the bundle only through the approved support channel.


## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before including any raw response, identifier, email, transcript excerpt, media URL, webhook payload, or production configuration.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- Redaction scan fails: do not transmit the bundle.
- Support requests a bearer key: refuse and use approved credential-verification steps.
- Evidence cannot reproduce the issue: add safe timing or code metadata, not meeting content.

## Examples

- "Review fireflies privacy-safe diagnostic bundle" produces a bounded plan and redacted receipt.
- A request that widens access or mutates production is paused at the approval boundary.


## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
