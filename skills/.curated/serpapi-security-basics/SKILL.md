---
name: serpapi-security-basics
description: 'Threat-model SerpAPI credentials, query data, result retention, browser exposure, logs, and ZeroTrace tradeoffs. Use when reviewing or hardening a search integration. Trigger with "secure a SerpAPI integration".'
argument-hint: "[application] [data-classification]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, serpapi, security, privacy, secrets]
model: inherit
effort: high
compatibility: Designed for Claude Code; key rotation, ZeroTrace enablement, retention changes, and production proxy changes require security and account-owner approval
---
# SerpAPI Security and Privacy Controls

## Overview

Protect the private key and treat queries, parameters, raw results, archive records, fixtures, and telemetry as potentially sensitive data.

## Prerequisites

- Application and data-flow inventory, data classification, threat model, and retention policy
- Account plan and entitlement evidence for any privacy feature
- Owners for secrets, application security, privacy, logging, and incident response

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect secret flow, browser bundles, logs, caches, and fixtures, `WebFetch` to verify current security and retention claims, and `Write` or `Edit` for server-side boundaries, redaction, tests, and evidence.

## Current Contract

SerpAPI requires a private API key and recommends server-side use for web applications. Standard search data is documented as expiring after 31 days. Enterprise ZeroTrace mode uses `zero_trace=true` to skip storing search parameters, files, and metadata, which also removes archive-based debugging; eligibility and exact guarantees must be rechecked against the account contract.

## Authentication

Keep `SERPAPI_KEY` in an approved server-side secret manager. Never ship it in browser or mobile bundles, accept it from end users, include it in URLs that are logged, or return Account API data to unauthenticated clients.

## Instructions

1. Map the key from secret store to client and prove it cannot reach source, client bundles, logs, traces, caches, fixtures, errors, or support exports.
2. Classify queries and results, document permitted purposes, and reject disallowed or unnecessarily sensitive input before search.
3. Expose an application-specific backend endpoint with authenticated callers, input allowlists, output minimization, rate limiting, and abuse monitoring.
4. Strip key-bearing URLs and unneeded raw result fields before persistence; set cache and log retention from policy rather than convenience.
5. Decide whether standard archive/debug behavior or ZeroTrace better matches the data class; do not combine ZeroTrace with a workflow that requires archive replay.
6. Test unauthorized callers, parameter injection, quota abuse, log leakage, fixture leakage, dependency compromise, and key revocation.
7. Present rotation, ZeroTrace, retention, or production-boundary changes for approval and retain a redacted control receipt.

## Approval Boundaries

Do not rotate a key, enable account features, change production retention, expose a proxy, or process a new sensitive data class without named owner approval.

## Output

Return the threat model, secret-flow proof, data classification, proxy controls, retention/ZeroTrace decision, negative-test results, approval record, and incident/rotation owners.

## Error Handling

| Condition | Response |
|---|---|
| Key appears in history or telemetry | Revoke or rotate under incident procedure and purge authorized copies. |
| Browser bundle references the key | Block release and move the call behind an authenticated backend. |
| Sensitive search used standard retention | Notify privacy/security owners and follow the approved deletion process. |
| ZeroTrace search needs archive debugging | Use local redacted evidence; do not assume an archive record exists. |

## Example

```text
key=server-secret-only; callers=authenticated; inputs=allowlisted; output=minimized; standard-retention=31-days; zero-trace=contract-reviewed; leakage-tests=pass
```

## Resources

- [SerpAPI security](https://serpapi.com/security)
- [ZeroTrace Mode](https://serpapi.com/zero-trace-mode)
- [Data retention and deletion](https://serpapi.com/legal#data-retention-and-deletion)

## Next Steps

Schedule a key-leak and public-endpoint abuse drill, then review the controls after any data-class change.
