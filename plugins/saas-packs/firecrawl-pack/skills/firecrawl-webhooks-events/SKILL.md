---
name: firecrawl-webhooks-events
description: >-
  Receive, verify, deduplicate, process, and reconcile current Firecrawl crawl, batch, extract, agent, and monitor webhooks. Use when building asynchronous event delivery. Trigger with "Firecrawl webhook", "X-Firecrawl-Signature", or "Firecrawl events".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <event-family>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, webhooks, security]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Signed Webhook Processing

## Overview

Treat a webhook as an authenticated delivery hint into a durable state machine. Verify before parsing or side effects, acknowledge promptly, and reconcile through status APIs after missed delivery.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Firecrawl signs the raw request body with HMAC-SHA256 in X-Firecrawl-Signature formatted sha256=hex. The documented events are crawl.started/page/completed; batch_scrape.started/page/completed; extract.started/completed/failed; agent.started/action/completed/failed/cancelled; monitor.page and monitor.check.completed. Endpoints must return 2xx within 10 seconds; failed delivery retries after 1, 5, and 15 minutes, then stops.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Register an HTTPS endpoint and choose only the events required for the workflow. Store the account webhook secret in an approved secret manager.
2. Capture the raw body before any JSON parser. Require one X-Firecrawl-Signature value, split and validate the sha256 prefix, hex-decode safely, and compare equal-length digests timing-safely.
3. Reject missing, malformed, or mismatched signatures before parsing, logging, queuing, or mutating state. Never treat a missing secret as verification success.
4. Parse the verified envelope, allowlist exact event types and schema, bind it to the expected team/job, and deduplicate by webhookId plus event/job context.
5. Persist an inbox record and respond with 2xx inside the deadline; process content and downstream writes asynchronously with tenant isolation and idempotency.
6. Handle page and terminal events according to their documented family. Do not wait for nonexistent crawl.failed or batch_scrape.failed events; reconcile job status and pagination.
7. Test signatures, raw-body mutation, duplicates, reordering, retry timing, unknown events, partial pages, crash recovery, and status reconciliation.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before creating the endpoint, storing a webhook secret, adding custom webhook headers/metadata, retaining page payloads, replaying production events, or changing event filters.

## Output

Return endpoint and event scope, secret reference, verification algorithm, schema/idempotency model, acknowledgment boundary, reconciliation path, test evidence, metrics, and replay/rollback controls.

## Error Handling

- Signature or raw body is unavailable: return a non-2xx rejection and perform no side effect.
- Processing fails after acknowledgment: retry from the durable inbox and reconcile provider state.
- Retries are exhausted or a terminal event is missing: poll the documented job status and paginate results.

## Examples

- "Add a crawl webhook" handles started/page/completed and reconciles status for failure.
- "Skip verification when the secret is unset" is explicitly rejected.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
