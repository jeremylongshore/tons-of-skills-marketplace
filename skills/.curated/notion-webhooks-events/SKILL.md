---
name: notion-webhooks-events
description: >-
  Implement verified Notion connection-webhook intake with deduplication, bounded processing, and fetch-current reconciliation. Use when reacting to workspace change signals. Trigger with "handle Notion webhooks", "verify Notion signature", or "reconcile Notion events".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<subscription> <event-scope> <processor>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, webhooks]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Webhook Intake and Reconciliation

## Overview

Implement verified Notion connection-webhook intake with deduplication, bounded processing, and fetch-current reconciliation.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Notion verifies a subscription with a one-time token and signs later raw request bodies in X-Notion-Signature using HMAC-SHA256. Events can aggregate, arrive out of order, and omit full changed content; fetch current state and reconcile. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Store verification material as a secret, hash the exact raw body, compare signatures in constant time, bind the subscription to the expected connection, and rotate through an approved recreate path.

## Instructions

1. Define subscribed event types, data owner, destination, retention, and current subscription API version.
2. Implement the verification handshake without logging or echoing the token beyond the required portal step.
3. Verify the raw-body signature before JSON parsing or queue acknowledgement.
4. Persist a deduplication key, event timestamp, entity identity, attempt, and processing state with tenant binding.
5. Acknowledge quickly, process asynchronously, fetch current state, and make downstream work idempotent.
6. Reconcile periodically for missed, aggregated, reordered, duplicated, or stale signals.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require workspace and data-owner approval to create, change, or delete a subscription; replay, backfill, and downstream writes require separate approval.

## Error Handling

- Reject missing or malformed signatures before parsing.
- Do not trust delivery order or use the event payload as full current content.
- Quarantine unknown event types while preserving a content-safe receipt.

## Output

Return the subscription contract, verification evidence, event-state model, deduplication policy, reconciliation plan, tests, and rotation runbook. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Reject a forged signature over a modified raw body.
- Process an out-of-order update by fetching and reconciling current state.

## Validation

Exercise and record these paths with expected and observed results:

- verification handshake
- valid signature
- forgery
- duplicate
- out of order
- reconciliation

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
