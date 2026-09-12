---
name: fireflies-multi-env-setup
description: >-
  Separate Fireflies development, staging, and production identities, webhook endpoints, secrets, quotas, fixtures, and observability. Use when preventing cross-environment leakage. Trigger with "Fireflies environments", "staging Fireflies", or "separate Fireflies keys".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, environments, security]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Multi-Environment Isolation

## Overview

Separate Fireflies development, staging, and production identities, webhook endpoints, secrets, quotas, fixtures, and observability. Prove isolation through configuration and failure-path evidence rather than environment names alone.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

Each environment should have an explicit Fireflies principal, API key, webhook signing secret, endpoint, allowed operations, event subscriptions, data policy, quota, and owner. Configuration names are not isolation if credentials or queues are shared.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Inventory every environment and its Fireflies user or team context.
2. Provision distinct bearer and signing secrets and prohibit production fallback.
3. Use environment-specific HTTPS webhook URLs, queues, stores, and dead letters.
4. Allow only synthetic data in development and reviewed test records in staging.
5. Validate configuration at startup without logging secret values.
6. Tag content-free metrics with environment and operation, never meeting identity.
7. Test rotation and rollback independently in each environment.


## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before connecting non-production to production Fireflies data, sharing credentials, or changing a production webhook endpoint.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- Credential belongs to the wrong team: fail startup.
- Webhook delivered to the wrong environment: quarantine and investigate without fetching data.
- Missing environment setting: do not silently fall back to production.

## Examples

- "Review fireflies multi-environment isolation" produces a bounded plan and redacted receipt.
- A request that widens access or mutates production is paused at the approval boundary.


## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
