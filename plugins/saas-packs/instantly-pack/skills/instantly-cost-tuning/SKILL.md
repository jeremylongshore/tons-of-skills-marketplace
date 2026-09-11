---
name: instantly-cost-tuning
description: >-
  Measure Instantly plan, account, verification, and enrichment usage without embedding stale prices. Use when reviewing workspace consumption or preparing a plan-capacity decision. Trigger with "audit Instantly usage", "estimate Instantly capacity", or "review Instantly plan consumption".
argument-hint: "[billing-period] [workspace]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- cost-tuning
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Instantly Cost and Capacity Governance

## Overview

Produce an evidence-backed capacity and spend recommendation using live workspace billing and pricing sources. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- Pricing and entitlements are dynamic; never hard-code a monthly price or account allowance.
- Workspace billing endpoints require workspace_billing read scope.
- Some endpoints publish independent limits or credit costs, so general API throughput is not a spend model.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Define the billing period, business outcome, sending-account inventory, and cost owner.
2. Read current plan and subscription details with read-only billing scope when available.
3. Measure active versus idle accounts, campaign outcomes, verification, and enrichment consumption.
4. Fetch current first-party pricing and contract terms before making a recommendation.
5. Model keep, consolidate, and expand options with assumptions and sensitivity ranges.
6. Require owner approval for plan, account, domain, or paid-enrichment changes.

## Approval Boundaries

Do not create, rotate, reveal, or revoke keys; invite or remove members; delegate across workspaces; connect sending accounts; create or activate campaigns; import or delete leads; change suppression or retention; register, patch, resume, or delete webhooks; alter plans or paid capacity; transmit diagnostics; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace-safe scope, files and contracts inspected, exact API v2 routes and required scopes, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| `401` | Stop and verify that the bearer key exists, is current, and was not revoked. |
| `403` | Stop and compare the operation with its exact required scope; do not broaden to `all:all` by default. |
| `429` | Coordinate the workspace-wide budget, honor endpoint overrides, and bound retries. |
| Schema or tenant mismatch | Fail closed, preserve redacted evidence, and do not retry a mutation. |

## Examples

Use a compact handoff that makes scope, mutation authority, and evidence reviewable.

Input:

```text
period=last-30-days; objective=cost-per-qualified-reply
```

Expected handoff:

```text
baseline=measured; options=3; prices=live-sourced; decision=awaiting-owner
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
