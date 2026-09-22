---
name: serpapi-debug-bundle
description: 'Assemble a privacy-safe SerpAPI support bundle with account capacity, search metadata, client context, and reproduction evidence. Use when local diagnosis is insufficient. Trigger with "build a SerpAPI debug bundle".'
argument-hint: "[search-id] [incident-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit, Bash(python3:*)
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, serpapi, debugging, support, privacy]
model: inherit
effort: high
compatibility: Designed for Claude Code; account/archive reads and reproduction searches require authorization and privacy review
---
# SerpAPI Privacy-Safe Debug Bundle

## Overview

Collect enough evidence to reproduce or escalate an issue while excluding credentials, sensitive queries, and unnecessary result data.

## Prerequisites

- Incident window, affected engine, search ID if available, and an incident owner
- Data classification and approval for any query or result disclosure
- Current client version, runtime, deployment, and retry configuration

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to trace code and logs, `WebFetch` to verify status and support contracts, `Write` or `Edit` for the redacted bundle, and `Bash(python3:*)` only for approved Account API or archive diagnostics.

## Current Contract

Account API supplies plan usage and hourly throughput without consuming monthly searches. Standard search records expire after the documented retention period; archive access can return 410 after deletion. ZeroTrace searches intentionally have no archive record and are harder to debug.

## Authentication

Load `SERPAPI_KEY` only in the diagnostic process. Remove `api_key`, key-bearing URLs, account email and ID, sensitive query values, raw HTML, and unrelated results before saving or sharing the bundle.

## Instructions

1. Freeze the time window and record safe runtime, client, deployment, engine, timeout, retry, and region facts.
2. Extract HTTP status, top-level error, search status, search ID, timing, and parameter names from existing evidence.
3. With approval, query Account API and retain only searches left, current usage, current/hourly usage, and account throughput.
4. Retrieve an archive record only when it exists, remains within retention, and its data classification permits access.
5. Reproduce against a sanitized fixture first; perform one bounded live reproduction only if necessary and approved.
6. Run automated and human redaction checks, create a manifest with hashes, and keep the raw working material in the approved incident boundary.
7. Share the smallest bundle needed for support and record recipient, purpose, retention, and deletion date.

## Output

Return a bundle manifest, redacted context and metadata, Account API capacity snapshot, fixture/live reproduction result, hashes, redaction evidence, and support handoff owner.

## Error Handling

| Condition | Response |
|---|---|
| Search ID is absent | Diagnose from safe local evidence; do not invent an archive lookup. |
| Archive returns 410 | Record expiry and request approval before reproducing the search. |
| Search used ZeroTrace | State that no archive is expected and rely on local redacted evidence. |
| Redaction cannot be proven | Do not export the bundle. |

## Example

```text
incident=SERP-42; engine=google; http=503; search_id=present; account_capacity=healthy; fixture=reproduced; live_replay=not-needed; secrets=0; bundle_sha256=recorded
```

## Resources

- [Account API](https://serpapi.com/account-api)
- [Searches Archive API](https://serpapi.com/searches-archive-api)
- [ZeroTrace Mode](https://serpapi.com/zero-trace-mode)
- [SerpAPI support](https://serpapi.com/contact)

## Next Steps

Delete the shared bundle on schedule and convert the resolved failure into a sanitized regression fixture.
