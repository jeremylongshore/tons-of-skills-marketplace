---
name: fireflies-common-errors
description: >-
  Diagnose Fireflies transport, GraphQL, permission, plan, processing, and operation-limit failures without unsafe retries or data probing. Use when an integration fails or returns partial data. Trigger with "Fireflies error", "too_many_requests", or "object_not_found Fireflies".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, errors, troubleshooting]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Error Taxonomy and Recovery

## Overview

Diagnose Fireflies transport, GraphQL, permission, plan, processing, and operation-limit failures without unsafe retries or data probing.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

Separate HTTP failures from top-level GraphQL errors and domain state. Normalize auth_failed, object_not_found, invalid_args or invalid_arguments, require_elevated_privilege, require_ai_credits, too_many_requests, unsupported_platform, and processing-state nulls.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Capture operation name, HTTP status, safe GraphQL error code, retryAfter, request ID, and timing.
2. Classify the failure before changing queries, permissions, or retry behavior.
3. For object_not_found, validate authorization and ID without enumeration.
4. For privilege or credit errors, stop and route to the accountable owner.
5. For throttling, honor retryAfter and the operation-specific limit.
6. Reproduce with synthetic variables or metadata-only selections.
7. Return a redacted diagnosis and the smallest safe next action.


## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before changing roles, plans, keys, privacy, meeting access, or replaying a mutation. Preserve the failing state and present the exact proposed change before acting.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- Unknown error text: preserve the code and safe metadata, then consult current error docs.
- HTTP 200 with errors: fail the operation rather than ignoring the errors array.
- Repeated retry failure: open an incident instead of widening backoff indefinitely.

## Examples

- "Review fireflies error taxonomy and recovery" produces a bounded plan and redacted receipt.
- A request that widens access or mutates production is paused at the approval boundary.


## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
