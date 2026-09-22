---
name: adobe-webhooks-events
description: >-
  Implement Adobe I/O Events registration, challenge validation, authentic delivery, idempotent enqueue, replay operations, and disablement recovery. Use when the task requires adobe i/o events authentic delivery. Trigger with "Adobe webhook", "Adobe I/O Events", or "verify Adobe event".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<event-provider> <registration> <consumer>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, events]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe I/O Events Authentic Delivery

## Overview

Implement Adobe I/O Events registration, challenge validation, authentic delivery, idempotent enqueue, replay operations, and disablement recovery. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

Webhook endpoints are public HTTPS and must echo the GET challenge during registration. Event delivery is at least once and may duplicate or arrive out of order. Validate recipientclientid plus the digital signature/public key from a validated static.adobeioevents.com URL, or use an approved mTLS configuration. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Use an entitled Developer Console project and least-privilege credential for registration administration. Delivery handlers never receive or log management credentials.

## Instructions

1. Resolve provider, event codes, organization/project/workspace, registration owner, endpoint, and data classification.
2. Validate the Registration API schema from current docs; do not copy a remembered payload or integration route.
3. Implement a narrow GET challenge response and POST size/type/schema checks before business processing.
4. Verify recipient client ID and signature/key allowlist or mTLS, then deduplicate on event identity before enqueue.
5. Acknowledge quickly; process asynchronously with ordering-aware state, retry budgets, DLQ, and replay controls.
6. Monitor retries and journal/recovery windows, manually re-enable disabled registrations, and reconcile gaps.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Security approves public ingress and authenticity method; product owner approves provider/events; operations approves replay. Registration replacement, re-enable, replay, or deletion requires explicit action approval.

## Error Handling

- Reject arbitrary public-key hosts and recipient mismatches.
- Do not assume ordering or exactly-once delivery.
- Do not hide a disabled registration behind successful endpoint health.

## Output

Return registration evidence, endpoint/authenticity contract, event ledger, dedupe/retry policy, replay runbook, monitoring, and gaps. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Accept and echo a valid challenge without exposing configuration.
- Reject a duplicate and a forged key URL before business processing.

## Validation

Exercise and record expected and observed results for:

- challenge
- valid signature
- recipient mismatch
- duplicate
- out of order
- disabled/replay

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
