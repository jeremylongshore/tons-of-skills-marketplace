---
name: firecrawl-ci-integration
description: >-
  Build deterministic CI gates for a Firecrawl v2 integration using synthetic fixtures, pinned schemas, secret scanning, and an optional protected smoke test. Use when adding regression coverage or release controls. Trigger with "Firecrawl CI", "Firecrawl contract tests", or "test our Firecrawl integration".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> [unit|contract|smoke]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, ci, testing]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl CI Contract

## Overview

Prove request construction, response handling, pagination, redaction, retries, and policy enforcement without spending credits or exposing production targets in routine pull-request CI.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Pin a reviewed Firecrawl v2 OpenAPI or SDK commit for contract tests. Cover SDK direct-data responses separately from REST success/data envelopes. Treat retryability, webhook event names, and pagination cursors as contract assertions rather than loose snapshots.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Inspect the repository runtime, package manager, existing test framework, generated-client policy, CI trust model, and secret-scanning controls.
2. Create synthetic fixtures for scrape documents, captured origin error pages, paginated crawl and batch results, validation failures, 402, 403, 429, and retryable server errors.
3. Add unit tests for request shaping, explicit crawl limits, URL policy, redaction, cache and retention choices, Retry-After parsing, bounded retries, cancellation, and idempotency.
4. Pin the v2 contract source and fail on incompatible endpoint, auth, required-field, event, or response-shape drift. Review intentional changes before updating the pin.
5. Run static analysis, unit tests, contract tests, secret scanning, and artifact inspection on untrusted pull requests with fake credentials only.
6. If live validation is justified, place one read-only synthetic canary behind a protected environment, disable it for forks, cap its credits and duration, and discard content bodies.
7. Make required failures fail closed and emit a receipt with the contract pin and exact test result.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before adding dependencies, updating the contract pin, enabling networked CI, granting a CI secret, changing required checks, or retaining a live response.

## Output

Return CI stages, fixture policy, contract source and pin, required checks, fork behavior, optional smoke-test boundary, test results, and any repository-setting changes still awaiting approval.

## Error Handling

- Contract changed: stop and present the reviewed diff instead of regenerating silently.
- Live smoke is unavailable: keep offline gates authoritative and report the smoke as skipped.
- Secret or captured content reaches an artifact: fail, quarantine, and remove the artifact.

## Examples

- "Test Firecrawl on fork PRs" produces offline synthetic tests with no secrets.
- "Add a production smoke test" requires a protected, read-only, capped environment and explicit approval.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
