---
name: fireflies-incident-runbook
description: >-
  Triage Fireflies auth, privacy, webhook, quota, data exposure, processing, and privileged-mutation incidents with containment and evidence boundaries. Use when responding during a live failure or suspected leak. Trigger with "Fireflies incident", "Fireflies outage", or "Fireflies data leak".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, incident-response, security]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Integration Incident Runbook

## Overview

Triage Fireflies auth, privacy, webhook, quota, data exposure, processing, and privileged-mutation incidents with containment and evidence boundaries.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

Classify incidents by confidentiality, integrity, availability, and destructive impact. Containment may mean disabling a consumer, revoking a key, pausing a queue, rejecting webhooks, or blocking mutations; preserve content-free evidence and coordinate destructive actions.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Declare an owner, severity, affected environment, timeline, and known operation or event family.
2. Contain the smallest boundary: caller, key, webhook endpoint, queue, worker, or mutation feature.
3. Preserve redacted logs, request IDs, GraphQL codes, signature results, deployments, and configuration revisions.
4. Determine whether meeting data, bearer keys, signing secrets, roles, privacy, shares, channels, or deletions were affected.
5. Rotate secrets or disable access only through the accountable owner and record the action.
6. Recover with synthetic or metadata-only probes and bounded traffic.
7. Document root cause, affected records through an approved channel, corrective actions, and follow-up tests.


## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before revoking production access, replaying events, restoring data, changing privacy or roles, notifying external parties, or deleting evidence.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- Potential secret exposure: prioritize containment and audit over routine debugging.
- Unknown mutation outcome: reconcile state before replay.
- Meeting content appears in a general incident channel: move to the approved restricted process.

## Examples

- "Review fireflies integration incident runbook" produces a bounded plan and redacted receipt.
- A request that widens access or mutates production is paused at the approval boundary.


## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
