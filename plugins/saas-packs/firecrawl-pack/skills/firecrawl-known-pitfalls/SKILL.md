---
name: firecrawl-known-pitfalls
description: >-
  Audit a Firecrawl integration for legacy v1 calls, unbounded crawls, incomplete pagination, unsafe retries, retention mistakes, and untrusted-content handling. Use when reviewing code or onboarding maintainers. Trigger with "Firecrawl pitfalls", "review Firecrawl code", or "Firecrawl anti-patterns".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> [changed-files]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, review, reliability]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Integration Pitfall Review

## Overview

Find high-impact failure modes before production. Tie every finding to current Firecrawl behavior and repository evidence instead of applying a generic checklist.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Common current hazards include legacy scrapeUrl/crawlUrl method names, implicit crawl scope, confusing API success with origin status, dropping pagination, retrying 4xx errors, assuming one credit per request, trusting scraped instructions, enabling cache on sensitive data, skipping webhook HMAC verification, and exposing the self-host quickstart.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Locate Firecrawl dependencies, imports, wrapper clients, REST paths, config, queues, webhooks, stores, tests, and deployment files.
2. Flag legacy v0/v1 routes or FirecrawlApp-style methods unless they are intentionally isolated behind the documented feature-frozen compatibility surface.
3. Find every crawl, batch, search, agent, and browser call. Require explicit scope, credit/time limits, cancellation ownership, and environment policy.
4. Verify SDK versus REST response handling, metadata.statusCode checks, complete pagination, terminal-state handling, and idempotent webhook processing.
5. Compare retry logic with the official error catalog. Reject retries for auth, credits, restrictions, validation, and other non-retryable failures.
6. Trace scraped or extracted content into logs, prompts, stores, and actions. Require sanitization, provenance, prompt-injection boundaries, retention, and deletion.
7. Rank findings by exploitability and impact, propose minimal fixes and regression tests, and verify the corrected paths.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before changing dependencies, expanding crawl scope, enabling raw formats/actions, weakening cache or retention safeguards, or auto-fixing production code.

## Output

Return evidence-linked findings, severity, affected paths, current contract, recommended patch, tests, approvals, and residual risk. Report clean controls as evidence, not as a blanket assurance.

## Error Handling

- Current docs disagree with installed types: pin both versions and resolve the discrepancy before editing.
- The target policy is missing: report the missing authority rather than assuming scraping is allowed.
- A fix would change behavior broadly: isolate it behind a canary and rollback boundary.

## Examples

- "Review our Firecrawl wrapper" checks v2 methods, pagination, retries, provenance, and data boundaries.
- "All requests return 200" still fails if captured documents have metadata.statusCode errors.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
