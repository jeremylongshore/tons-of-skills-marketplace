---
name: fireflies-deploy-integration
description: >-
  Deploy a Fireflies GraphQL worker or Webhooks V2 receiver with managed secrets, raw-body verification, bounded queues, and reversible rollout. Use when shipping to a hosted runtime. Trigger with "deploy Fireflies integration", "host Fireflies webhook", or "Fireflies deployment".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, deployment, webhooks]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Deployment and Webhook Boundary

## Overview

Deploy a Fireflies GraphQL worker or Webhooks V2 receiver with managed secrets, raw-body verification, bounded queues, and reversible rollout.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

Outbound GraphQL needs a server-side bearer key. Inbound Webhooks V2 needs HTTPS, optional but strongly recommended signing-secret verification over the raw body, a 2xx response within 10 seconds, and durable asynchronous work after acknowledgement.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Define the exact runtime, regions, data boundary, operations, events, and owners.
2. Provision separate API and webhook secrets through the platform secret manager.
3. Preserve raw request bytes until HMAC verification and parse only after success.
4. Acknowledge valid events within 10 seconds and enqueue idempotent downstream work.
5. Set timeouts, concurrency, quotas, dead-letter handling, and content-free logs.
6. Roll out to staging with synthetic events, then canary production traffic.
7. Verify disablement, secret rotation, queue drain, and rollback receipts.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before production deployment, DNS or webhook endpoint changes, secret rotation, event subscription changes, or replaying dead-lettered content.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- Signature unavailable or invalid: reject rather than processing optimistically.
- Acknowledgement exceeds 10 seconds: move work behind the queue.
- Rollback leaves queued jobs active: pause consumers and reconcile safely.

## Examples

- "Review fireflies deployment and webhook boundary" produces a bounded plan and redacted receipt.
- A request that widens access or mutates production is paused at the approval boundary.

## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
