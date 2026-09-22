---
name: bamboohr-hello-world
description: >-
  Prove a BambooHR tenant connection with one minimal, low-sensitivity request
  and a redacted receipt. Use when starting an integration or isolating host,
  credential, and permission failures. Trigger with "BambooHR hello world",
  "test BambooHR connection", or "first BambooHR request".
allowed-tools: Read,Glob,Grep,Write,Edit,Bash(curl:*)
argument-hint: "<tenant-subdomain> [oauth|api-key]"
version: 1.5.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, hr, bamboohr, quickstart, connectivity]
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# BambooHR Minimal Connection Proof

## Overview

Verify routing, TLS, authentication, and basic permission with the smallest
useful call. Do not begin with the employee directory: it contains personal data
and is unnecessary for a connectivity test.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The tenant, identity, and data scope only when approved live work is in scope.
- The current evidence register plus customer-specific permissions and agreements.

## Current Contract

Use the tenant-local host `https://company-subdomain.bamboohr.com`. The official
OpenAPI operation `GET /api/v1/company_information` returns basic company
profile information and supports OAuth or API-key authentication.

## Authentication

Prefer a short-lived OAuth access token for partner integrations. For an
internal API key, Basic auth uses the API key as username and `x` as password.
Load secrets from the current process environment or an approved secret manager;
never place a token directly in the command, URL, source file, or receipt.

## Instructions

1. Confirm the exact tenant subdomain and auth mode. Reject slashes, schemes,
   ports, and dots in the subdomain input.
2. Inspect the project for an existing BambooHR client and reuse its timeout,
   user-agent, request-ID, and redaction controls.
3. If an operator approves a direct API-key smoke test, run a body-discarding
   request:

   ```bash
   curl --fail-with-body --silent --show-error \
     --max-time 20 --output /dev/null --write-out '%{http_code}\n' \
     --user "${BAMBOOHR_API_KEY}:x" \
     "https://${BAMBOOHR_COMPANY_SUBDOMAIN}.bamboohr.com/api/v1/company_information"
   ```

4. For OAuth, send `Authorization: Bearer …` from the application's secret-
   aware HTTP client rather than echoing a token through shell history.
5. Record timestamp, tenant alias, auth mode, HTTP status, elapsed time, and a
   server request ID when available. Do not retain the response body.
6. Only after the connection proof succeeds, request approval for an employee-
   scoped test with an explicitly minimized field list.

## Tool Discipline

Use Read, Glob, and Grep to find current client and configuration conventions.
Use Write/Edit only to add an approved example or test. Bash is restricted to
`curl`; show the exact host and body-retention behavior before executing it.

## Safety Justification

The optional live request can reach sensitive HR infrastructure. It is limited
to HTTPS, one read-only company-information endpoint, a finite timeout, no body
retention, and operator approval for the tenant and credential.

## Approval Boundaries

Do not make a live request, access an employee endpoint, install a package, or
write credentials without explicit approval. A successful `200` proves only
this identity can perform this operation; it does not prove broader access.

## Output

Return a PASS/FAIL receipt with tenant alias, endpoint class, auth mode, status,
latency, request ID, redaction confirmation, and the next narrow test.

## Error Handling

- DNS/TLS failure: verify the tenant subdomain and trust path.
- `401`: validate credential type and freshness without printing it.
- `403`: the identity lacks the operation; do not escalate permissions silently.
- `429`, `504`, or `598`: report the transient condition and defer to the retry skill.

## Examples

- "Test our BambooHR setup" produces a proposed body-discarding company-info check.
- "Dump the directory to prove it works" is narrowed to the connection proof.

## Resources

Read [official evidence](references/official-docs.md) before running the smoke test.
