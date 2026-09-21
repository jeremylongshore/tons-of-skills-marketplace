---
name: mistral-install-auth
description: >-
  Establish Mistral API access with server-side credentials, workspace ownership, and revocation evidence. Use when installing or auditing a Mistral environment. Trigger with "set up Mistral", "configure a Mistral key", or "audit Mistral authentication".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<runtime> <workspace> <environment>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, authentication]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral Authentication and Installation

## Overview

Create a reviewable authentication boundary before any inference call. Separate workspace access, secret custody, application authorization, and billing so possession of a key never implies permission to spend or process arbitrary data.

## Prerequisites

- A named workspace administrator, application owner, and spend owner.
- An approved server-side secret manager and environment-specific rollback route.
- A runtime and official client selected from current first-party documentation.

## Current Contract

Mistral API requests use Bearer authentication at `https://api.mistral.ai`. Studio-created keys are displayed once. Free mode can include usage; current billing and limits must be read from the account rather than encoded.

## Authentication

Store the credential as `MISTRAL_API_KEY` and send it only in the `Authorization: Bearer` header from a trusted server. Never place it in source, browser bundles, URLs, prompts, logs, screenshots, fixtures, or support archives.

## Instructions

1. Inventory the workspace, runtime, environment, data class, volume, and accountable owners.
2. Confirm the administrator permitted to create and revoke an environment-scoped key.
3. Capture the one-time key directly into the approved secret manager and configure only its reference.
4. Pin the client dependency and API host without recording the secret value.
5. Validate configuration offline; request approval before one synthetic live call.
6. Record ownership, creation date, rotation route, live-check receipt, and rollback readiness.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Require explicit approval for key creation or revocation, billing or role changes, live requests, deployments, or customer-derived content.

## Error Handling

- A `401` usually indicates a missing, malformed, revoked, or wrong-environment key.
- A valid key can still fail because the workspace is suspended or at a current rate/spend boundary.
- Any browser or log exposure is an incident: revoke, rotate consumers, and verify history removal.

## Output

Return workspace, environment, secret-reference name, host, client pin, owner, validation state, evidence IDs, risks, and rollback. Exclude credentials and content.

## Examples

- Prepare a Python service with an injected production secret and no live request.
- Report `environment=staging; auth=Bearer; live_smoke=awaiting-approval`.

## Validation

Confirm host/header, scan tracked output for secrets, prove no browser exposure, and verify the owner can revoke the key.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
