---
name: procore-hello-world
description: >-
  Prove a Procore connection with a read-only, company-routed smoke test before enabling mutations. Use when verifying a new token, app installation, DMSA project scope, environment, or deployment. Trigger with: "test my Procore connection", "run a Procore smoke test", "verify Procore access".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[environment-and-company-id]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - smoke-test
  - connectivity
compatibility: 'Requires a valid Procore OAuth Bearer token and read access to at least one permitted company or project.'
---

# Procore Read-Only Connection Proof

## Overview

Establish identity, company routing, project visibility, and pagination without creating construction records. The proof must demonstrate the selected environment and permission boundary, not merely that an access token exists.

## Prerequisites

- Approved OAuth token obtained through the intended grant and environment
- Expected company identifier and at least one known permitted project
- Redacted evidence destination and named owner for permission failures

## Instructions

### Step 1: Freeze the target

Record the expected environment, API base, company ID, token alias, and app version. Reject mixed production and sandbox inputs before sending a request.

### Step 2: Verify identity

Call the documented current-user or company discovery surface using the Bearer token. Supply `Procore-Company-Id` when the contract requires company routing, especially for multi-region and DMSA traffic.

### Step 3: List visible projects

Use the documented projects list endpoint and a small page. Follow the returned pagination contract instead of assuming one page is complete.

### Step 4: Assert the boundary

Confirm the known permitted project appears and a known unpermitted project does not. Treat excess visibility as a security defect rather than a successful smoke test.

### Step 5: Capture a receipt

Record status, normalized route, company and project identifiers, page metadata, response latency, and a hash of the sanitized assertion output. Do not retain names or payloads unless the test requires them.

## Authentication

Authenticate with an OAuth 2.0 Bearer token produced for the selected Procore environment. The token carries either user permissions or DMSA permissions; the smoke test never broadens those permissions.

## Tool Discipline

Use Read and Grep to inspect environment configuration and expected identifiers. Use Write or Edit only for the approved test, assertion fixture, or redacted receipt; this workflow must not create, update, or delete Procore records.

## Output

- Environment and identity assertion
- Company-routing and permitted-project assertion
- Pagination and negative-access assertion

Return pass or fail with the exact failed boundary and a secret-free receipt.

## Examples

After a customer installs a DMSA app, the operator lists projects for that company and confirms the selected pilot project is visible. The test also confirms a non-permitted project is absent before the deployment is allowed to process events.

## Error Handling

| Failure | Response |
| --- | --- |
| 401 response | Verify token expiry, environment, revocation, and authorization header construction. |
| 403 or unexpected 404 | Check app connection, DMSA permissions, permitted projects, and enabled tools. |
| Empty project list | Validate company routing and the principal's project membership before expanding access. |
| Unexpected project visible | Stop deployment and reduce the user or DMSA permission boundary. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Making your first API call](https://developers.procore.com/documentation/making-first-call)
- [Client Credentials test call](https://developers.procore.com/documentation/oauth-client-credentials)
- [Pagination](https://developers.procore.com/documentation/pagination)
