---
name: firecrawl-local-dev-loop
description: >-
  Build a deterministic Firecrawl development loop with SDK fakes, recorded synthetic contracts, and an optional trusted-network self-hosted stack. Use when developing without production data or routine Cloud spend. Trigger with "Firecrawl local dev", "mock Firecrawl", or "self-host Firecrawl locally".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> [mock|self-host]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, local-development, testing]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Local Development Loop

## Overview

Keep routine development offline and deterministic. Use self-hosting only when behavior must be exercised end to end, and treat the official Compose quickstart as a local evaluation stack.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

The current self-host guide pins a specific verified release, exposes the API on localhost port 3002, and disables database authentication for its first-run baseline. It explicitly lacks production authentication, durable storage, TLS, high availability, and several Cloud capabilities. Its release and Compose contract must be re-read before use.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Inspect the application runtime, official SDK version, wrapper boundary, test framework, and operations the integration actually uses.
2. Define typed adapter interfaces for scrape, crawl submission/status, batch, map/search, and any other required methods so tests do not mock internals.
3. Create synthetic fixtures for direct SDK documents, REST envelopes, origin error pages, paginated jobs, throttling, credits, policy denial, invalid extraction, and webhook signatures.
4. Run unit and contract tests against fakes by default. Prohibit production keys, real customer URLs, captured bodies, and external network access.
5. When end-to-end behavior is necessary, follow the current official self-host guide at its pinned release on a trusted local network. Do not improvise a one-container substitute.
6. Verify readiness separately from one functional /v2/scrape, record unsupported features, and tear down or isolate the evaluation stack after use.
7. Keep lockfiles, fixtures, contract pins, and local setup instructions current; add a regression before fixing each discovered defect.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before starting Docker services, downloading a new release, using Cloud from local tests, capturing a real page, or retaining self-hosted databases.

## Output

Return adapter boundaries, fixture inventory, commands the operator should run, contract pin, self-host capability gaps, test results, network/secret posture, and cleanup state.

## Error Handling

- Fixture drifts from the pinned contract: update through review, not from a live production payload.
- Self-host stack is reachable outside the trusted host: stop it and correct network controls.
- A Cloud-only feature is required: use a protected test environment instead of pretending local parity.

## Examples

- "Mock Firecrawl crawl status" adds paginated and terminal synthetic fixtures at the adapter.
- "Use the local quickstart in production" is rejected because the documented baseline disables critical controls.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
