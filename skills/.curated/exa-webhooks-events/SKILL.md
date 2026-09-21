---
name: exa-webhooks-events
description: >-
  Receive Exa Monitor events through verified signatures, replay resistance, deduplication, and fast acknowledgment. Use when operating or reviewing this Exa boundary. Trigger with "Exa webhooks events", "review Exa webhooks events", or "fix Exa webhooks events".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<monitor-id> <receiver-route>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Monitor Webhook Processing

## Overview

Receive Exa Monitor events through verified signatures, replay resistance, deduplication, and fast acknowledgment. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Monitors schedule recurring searches, deduplicate prior results, and deliver to an HTTPS public webhook. The one-time webhookSecret is returned only when a Monitor is created. Exa-Signature carries timestamp and v1 values for HMAC-SHA256 verification over the signed payload; redirects are not followed.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Create or rotate a Monitor only with an approved query, schedule, destination, and budget.
2. Store the one-time webhook secret immediately in the receiver secret store.
3. Verify the raw body timestamp and HMAC using constant-time comparison before parsing.
4. Reject stale, malformed, unsigned, redirected, or unrecognized deliveries.
5. Deduplicate on stable event and run identifiers, acknowledge quickly, and enqueue work.
6. Reconcile webhook processing with the Monitor run API and retain content-free evidence.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Never reconstruct a signature from reserialized JSON.
- The secret cannot be fetched later if it was not stored at creation.
- Webhook receipt alone does not prove downstream processing or a completed Monitor run.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Verify Exa-Signature against the raw request body, persist the event ID, enqueue processing, and reconcile the associated run.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
