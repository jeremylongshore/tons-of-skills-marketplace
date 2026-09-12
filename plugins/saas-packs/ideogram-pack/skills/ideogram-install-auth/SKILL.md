---
name: ideogram-install-auth
description: >-
  Configure Ideogram API access with prepaid billing, server-side credentials, and explicit team ownership. Use when installing or auditing a new Ideogram environment. Trigger with "set up Ideogram API", "configure an Ideogram key", or "audit Ideogram authentication".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<runtime> <team> <environment>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, authentication]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Ideogram work requires network access and prepaid API credit"
---
# Ideogram Authentication and Installation

## Overview

Establish a reviewable Ideogram API boundary before any paid generation runs. Separate developer-account enrollment, team ownership, billing, secret storage, and application authorization so a valid key never becomes accidental authority for a browser or untrusted tenant.

## Prerequisites

- A named Ideogram team Owner and accountable application owner.
- Accepted developer terms, a payment method, and positive prepaid API credit.
- A server-side secret manager and an environment-specific rollback plan.

## Current Contract

Ideogram API subscriptions and web-app subscriptions are billed separately. Keys are created in the API dashboard, displayed once, revocable, and shared against the team's credit balance. Team roles are Owner, Admin, and Member; multiple keys do not create separate balances.

## Authentication

Store the key as `IDEOGRAM_API_KEY` and send it only in the `Api-Key` header to `https://api.ideogram.ai`. Never place it in source control, URLs, browser bundles, prompts, logs, screenshots, or client telemetry. Treat application user authorization as a separate control.

## Instructions

1. Inventory the runtime, Ideogram team, environment, data class, expected concurrency, and spend owner.
2. Confirm developer terms, payment method, positive credit, and the team role allowed to create or revoke keys.
3. Create one environment-scoped key and capture it directly into the approved secret manager because it is shown once.
4. Configure the API host and secret reference without copying the value into repository files.
5. Validate configuration offline, then run one synthetic generation only when live spend and content are approved.
6. Record the key owner, creation date, rotation route, billing owner, validation result, and rollback state.

## Tool Discipline

Use Read, Glob, and Grep to inspect dependency, configuration, and deployment surfaces. Use Write and Edit only for approved configuration or documentation changes. Invocation alone does not authorize key creation, billing changes, team membership changes, paid generation, or deployment.

## Approval Boundaries

Require explicit ownership before adding credit, enabling auto-recharge, creating or revoking a key, changing a team role, sending sensitive prompts or images, or deploying a live integration. Repository inspection and synthetic offline validation remain read-only.

## Error Handling

- A `401` points first to a missing, malformed, revoked, or wrong-environment key.
- A syntactically valid key can still fail when the shared team balance lacks positive credit.
- A key exposed to a client or log is an incident: revoke it, rotate consumers, and verify removal from history.

## Output

Return the environment, team and role boundary, secret-manager reference name, API host, billing readiness, offline and live-check status, evidence identifiers, risks, and rollback state. Exclude the credential, prompts, images, expiring URLs, and customer data.

## Examples

- Configure a production worker with an injected secret reference and a distinct staging key.
- Report `environment=staging; auth=Api-Key; credit=positive; live_smoke=approved; rollback=key-revocation-ready`.

## Validation

Verify the header name and host, scan tracked files for accidental values, confirm no browser exposure, and check that the accountable owner can revoke the key. A successful generation is not sufficient if evidence retention or billing ownership is unresolved.

## Resources

- [Current first-party evidence map](references/official-docs.md) — use the dated endpoint, webhook, billing, team, and training links as the contract index for this workflow.
- Recheck the endpoint-specific page and current OpenAPI description before relying on an enum, limit, beta feature, or lifecycle claim.
- Record live observations as environment-specific evidence, not as universal vendor guarantees.
