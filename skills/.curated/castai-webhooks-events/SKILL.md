---
name: castai-webhooks-events
description: 'Design and operate CAST AI webhook notifications with explicit severity routing, schema tolerance, receiver security, deduplication, and audit-log reconciliation. Use when connecting CAST AI to an incident or operations system. Trigger with: "configure CAST AI webhooks", "route CAST AI notifications", "audit CAST AI events".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[receiver-and-notification-scope]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - kubernetes
  - cast-ai
  - webhooks
  - observability
compatibility: 'Requires CAST AI organization notification access and an HTTPS receiver governed by the target incident-management system'
---

# CAST AI Webhook Notification Lane

## Overview

Route only actionable CAST AI notifications to a hardened receiver. Treat the console-configured request template as the payload contract and the CAST AI Audit log as reconciliation evidence, not as a guessed public event schema.

## Prerequisites

- CAST AI organization, notification owner, severity policy, and receiver
- HTTPS endpoint with authentication, request limits, retention, and on-call ownership
- Sanitized sample template and failure fixture

## Instructions

### Step 1: Define the event contract

Use Read and Grep to identify required severity levels, cluster and organization scope, destination, payload fields, privacy classification, deduplication key, and escalation behavior. Exclude fields the receiver does not need.

### Step 2: Harden the receiver

Require TLS, an authenticated boundary appropriate to the chosen integration, bounded body size, content-type validation, request timeout, concurrency limit, replay resistance, redacted logs, and a durable queue. Do not claim CAST AI sends a signature or header unless the configured product flow documents it.

### Step 3: Configure the notification

In the CAST AI organization, create a webhook with a clear name, callback URL, severity triggers, and valid JSON request template. Use Write or Edit to version the receiver's expected template and schema tests without committing destination secrets.

### Step 4: Normalize and route

Parse required fields defensively, preserve unknown fields, normalize timestamps, derive a stable deduplication key from configured content, and map severity through an approved table. A notification should enrich an incident, not directly mutate CAST AI or Kubernetes.

### Step 5: Test all outcomes

Test valid, unknown-field, missing-optional-field, malformed, oversized, unauthorized, duplicate, delayed, and receiver-down cases. Verify bounded retry/queue behavior and that payloads or credentials do not leak into logs.

### Step 6: Reconcile with the Audit log

Use the CAST AI console Audit log to confirm user-initiated and automated policy operations around the test window. Record what the webhook delivered, what the audit view shows, and any known coverage gap.

## Tool Discipline

Use Read and Grep for receiver, runbook, and payload-contract discovery. Use Write and Edit for the versioned template, schema, tests, routing policy, and operational record. This skill does not create a live webhook or send test traffic without an approved external change.

## Output

- Severity, payload, and privacy contract
- Hardened receiver behavior and schema tests
- Deduplication, routing, and outage policy
- Webhook-versus-Audit-log reconciliation receipt

## Examples

A critical notification opens or enriches one incident using a stable configured identifier. Duplicate deliveries are acknowledged without duplicate pages, and unknown payload fields are retained safely rather than rejecting the event.

## Error Handling

| Failure                              | Response                                                        |
| ------------------------------------ | --------------------------------------------------------------- |
| Receiver authentication is undefined | Do not expose the endpoint                                      |
| Payload template is invalid JSON     | Reject configuration before activation                          |
| Destination is unavailable           | Queue within a bound, then alert on delivery failure            |
| Audit log and delivery disagree      | Record the gap and escalate before relying on complete coverage |

## Resources

- [Webhook evidence and source notes](references/official-docs.md)
- [Set up webhook notifications](https://docs.cast.ai/docs/setup-notification-webhook)
- [Audit log](https://docs.cast.ai/docs/audit-log)
- [API access](https://docs.cast.ai/docs/api-access)
