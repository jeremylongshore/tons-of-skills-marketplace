---
name: bamboohr-webhooks-events
description: >-
  Create and operate BambooHR event- or field-based webhooks with one-time key
  custody, HMAC-SHA256 verification, idempotency, and replay controls. Use when
  building employee-change delivery or diagnosing webhook failures. Trigger
  with "BambooHR webhook", "BambooHR events", or "BambooHR webhook signature".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<create|receive|audit> <event-or-field-scope>"
version: 1.5.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, hr, bamboohr, webhooks, security]
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# BambooHR Webhook Operations

## Overview

Operate permissioned BambooHR webhooks as a security boundary. The creation
response contains a `privateKey` used for HMAC-SHA256 and returns it only once;
losing it requires controlled replacement, not a retrieval call.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The tenant, identity, and data scope only when approved live work is in scope.
- The current evidence register plus customer-specific permissions and agreements.

## Current Contract

- Create/list/get/update/delete and log endpoints live under `/api/v1/webhooks`.
- The destination URL must use HTTPS and `format` is required (`json` or
  `form-encoded` in the reviewed OpenAPI).
- `monitorFields` is required when events include `employee.updated` or
  `employee_with_fields.updated`; omitted events default to field-based employee
  events that also require monitored fields.
- Receiver `4xx` responses are not retried. Receiver `5xx` responses may be
  retried up to five times at documented 5, 10, 20, 40, and 80 minute intervals.

## Authentication

Webhook management requires OAuth scope `webhooks` or a permitted API-key user.
Store the one-time `privateKey` immediately in a secret manager scoped to tenant
and webhook ID. Keep management credentials separate from receiver verification.

## Instructions

1. Choose event-based or field-based delivery and list only the events,
   `monitorFields`, and `postFields` needed by the consumer.
2. Validate an HTTPS destination and use a non-production receiver for creation
   tests. Prepare secret storage before the create call.
3. Capture `id` and `privateKey` from the `201` response atomically; store the key
   once and ensure it never enters logs, tickets, fixtures, or source control.
4. Implement HMAC-SHA256 over the exact raw request bytes according to BambooHR's
   current webhook documentation. Do not parse or reserialize before checking.
   Confirm the documented signature carrier/header from current docs or a
   controlled sample; this pack does not invent one.
5. Compare signatures in constant time, reject before processing, then enforce
   tenant routing, payload schema, event allowlist, timestamp/replay window when
   supplied, and an idempotency key derived from stable delivery facts.
6. Acknowledge only after durable enqueue. Return intentional `4xx` for terminal
   payload rejection and `5xx` only when a later retry can succeed.
7. Monitor webhook logs, last-fired time, verification failures, duplicates,
   queue age, and dead letters. Rotate by creating and validating a replacement
   before removing the old webhook.

## Tool Discipline

Use Read, Glob, and Grep to inspect receiver code and secret handling. Use
Write/Edit only for approved handler, tests, and runbook changes. This skill does
not authorize webhook creation, update, deletion, or receipt of production PII.

## Approval Boundaries

Require approval for event/field scope, destination, management identity, secret
write, create/update/delete calls, production traffic, and replay of any payload.

## Output

Return webhook type, event/field scope, destination class, verification contract,
secret custody receipt without value, idempotency strategy, receiver status
policy, test results, monitoring, and rotation procedure.

## Error Handling

- Creation response not stored atomically: delete or disable the unverified
  webhook and recreate under approval.
- Signature contract uncertain: fail closed and inspect current official docs.
- Repeated `5xx`: stop accepting new side effects, preserve queue evidence, and
  repair before BambooHR exhausts retries.

## Examples

- "Notify us when department changes" discovers the permitted field ID first.
- "Use a conventional signature header" is rejected until current official
  evidence confirms the exact carrier and signing input.

## Resources

Read [official evidence](references/official-docs.md) before webhook changes.
