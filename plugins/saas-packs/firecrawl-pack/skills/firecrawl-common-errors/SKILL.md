---
name: firecrawl-common-errors
description: >-
  Analyze and resolve current Firecrawl v2 validation, authentication, credit, policy, rate, concurrency, timeout, and server errors. Use when an API or SDK call fails. Trigger with "Firecrawl error", "Firecrawl 429", "Firecrawl 402", or "Firecrawl forbidden".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<status-or-error> [request-id]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, errors, troubleshooting]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Error Triage

## Overview

Translate an error into a safe next action using Firecrawl's published error catalog. Do not retry every non-success response and do not confuse a returned document with an origin error status for an API failure.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Non-2xx REST responses normally contain success false and an error string, sometimes details or code. The current retryable status set is 408, 429, 500, 502, 503, and 504; 422 is conditional. Authentication, insufficient-credit, restriction, and request-shape failures require correction rather than blind retry.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Capture the HTTP status, error string, optional code/details, request or job ID, operation, timestamp, SDK version, and a redacted request shape.
2. Check metadata.statusCode on returned documents. A captured 403 or 404 page consumes a result path and should not be handled like an API transport error.
3. For 400 or 422, validate the request against the current endpoint schema and simplify JSON extraction requirements before retrying.
4. For 401, verify secret injection and key selection without printing the key. For 402, stop work and route the credit or billing decision to the owner.
5. For 403, inspect plan entitlement, team ownership, endpoint/format key restrictions, IP restrictions, or policy controls; never bypass them with another uncontrolled key.
6. For 429, distinguish rate from concurrency pressure, honor Retry-After when available, reduce producers, and use queue status evidence.
7. For retryable timeouts or server failures, use bounded exponential backoff with jitter, then escalate with redacted IDs and timestamps.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before rotating credentials, enabling pay-as-you-go, upgrading a plan, relaxing a key/IP restriction, increasing concurrency, or sharing target details with support.

## Output

Return the exact classification, retryability decision, safe remediation, attempts used, affected scope, redacted evidence, escalation owner, and prevention test.

## Error Handling

- Unknown error: preserve its exact status and error string and compare with current docs or support.
- Error body cannot be parsed: fall back to status, headers, request ID, and bounded transport diagnostics.
- Retry budget is exhausted: stop and escalate; do not create an unbounded retry loop.

## Examples

- "Firecrawl returns 429" distinguishes team rate limits from browser concurrency and queue saturation.
- "A scrape succeeded with statusCode 403" treats it as captured origin content, not a successful source page.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
