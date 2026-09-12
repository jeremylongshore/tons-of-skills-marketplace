---
name: firecrawl-debug-bundle
description: >-
  Assemble a minimal, redacted Firecrawl diagnostic package for internal triage or vendor support. Use when a failure needs escalation without exposing keys or captured content. Trigger with "Firecrawl debug bundle", "Firecrawl support evidence", or "collect Firecrawl diagnostics".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<request-or-job-id> <output-directory>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, diagnostics, security]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Privacy-Safe Support Evidence

## Overview

Produce structured evidence that can reproduce or classify a failure without dumping the repository, environment, request headers, URLs, or response bodies.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Useful evidence includes SDK/runtime version, v2 operation, timestamps, opaque request/job/webhook IDs, HTTP status, documented error/code, queue/job state, pagination state, option names, and content-free metrics. Firecrawl support does not need a broad tarball or the API key.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Confirm the incident owner, destination, approved evidence fields, retention window, and whether target URLs themselves are sensitive.
2. Collect package/runtime versions, operating context, v2 endpoint or SDK method, UTC timestamps, and a normalized option-name list.
3. Record status, error/code/details after redaction, response headers on an allowlist, request/job/webhook IDs, queue state, pagination cursor presence, counts, sizes, timings, and metadata.statusCode distribution.
4. Represent URLs with approved host labels or salted hashes; never include credentials, cookies, Authorization, custom headers, page content, screenshots, uploaded bytes, prompts, or extracted values.
5. Run secret, token-pattern, URL-query, email, and content-leak scans over the proposed bundle. Manually inspect the exact files.
6. Create a manifest with file hashes, collector version, redaction policy, known omissions, recipient, expiry, and deletion owner.
7. Require recipient approval, transmit through the approved channel, and record deletion or ticket linkage.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before collecting from production, including a hostname or request option value, sharing outside the organization, or extending bundle retention.

## Output

Return a small manifest and redacted structured evidence files, scan results, omissions, recipient and purpose, expiry, hashes, and cleanup receipt. Do not create a repository or home-directory archive.

## Error Handling

- Redaction scan finds a secret or content fragment: quarantine and rebuild the bundle.
- Evidence cannot distinguish request from origin failure: add status and metadata distributions, not bodies.
- Support requests raw credentials or unrestricted content: refuse and escalate through the security owner.

## Examples

- "Prepare evidence for a crawl timeout" returns timings, state, IDs, and redacted option names.
- "Zip the whole repo and .env" is refused and replaced with a minimal allowlisted manifest.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
