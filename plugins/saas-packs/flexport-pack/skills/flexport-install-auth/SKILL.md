---
name: flexport-install-auth
description: >-
  Configure Flexport OAuth 2.0 client credentials or a deliberately accepted API key. Use when selecting endpoint scopes, creating credentials, caching access tokens, or rotating a compromised integration. Trigger with: "set up Flexport auth", "scope Flexport credentials", "cache Flexport token".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[workload-and-required-endpoints]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - authentication
  - oauth
compatibility: 'Requires a Flexport administrator, an approved secret store, and network access to api.flexport.com.'
---

# Flexport Credential and Token Boundary

## Overview

Prefer a distinct endpoint-scoped OAuth client for each workload. Treat broad API keys as an explicit exception, and budget token acquisition because client-credential tokens last 24 hours while token requests are limited to 10 per day.

## Prerequisites

- Named workload owner and exact endpoint inventory
- Flexport administrator access to API Credentials
- Secret store, redacted audit sink, and rotation procedure

## Instructions

### Step 1: Choose the credential type

Use OAuth client credentials for new integrations so endpoint resources can be selected. Accept an API key only after documenting why its broad access is necessary.

### Step 2: Create one credential per system

Separate production, non-production, and independent workloads. Flexport does not let operators add endpoints to an existing credential, so create a replacement when scope must expand.

### Step 3: Request a token once

POST to `/oauth/token` with `client_id`, `client_secret`, audience `https://api.flexport.com`, and grant type `client_credentials`. Never expose the secret in a browser, shell history, or receipt.

### Step 4: Cache by credential

Store the JWT and expiry in a concurrency-safe cache. Refresh before expiry with jitter and a single-flight lock; do not spend the 10-request daily token budget per business request.

### Step 5: Prove least privilege

Run one approved read against every required endpoint and one negative test against an endpoint outside the credential resource set.

### Step 6: Rotate without ambiguity

Create and validate a replacement, switch one workload, observe it, then revoke the old credential. Record only credential aliases, timestamps, and outcome.

## Authentication

REST calls authenticate with a cached OAuth 2.0 client-credentials Bearer token using audience `https://api.flexport.com`, or an explicitly accepted broad API key. Use distinct credentials per workload and never log credentials or tokens. MCP calls use the authenticated connection to `https://mcp.flexport.com/mcp` and remain subject to each tool's documented account permissions.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Flexport-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

Return a machine-reviewable receipt in this shape; adapt the operation values, but never place credentials or provider payloads in it:

```yaml
surface: rest-v3
operation: shipment-read
decision: approved
outcome: verified
evidence:
  release_sha: recorded-out-of-band
  provider_reference: redacted
rollback_owner: logistics-platform
```

## Examples

A shipment reader gets its own OAuth client for shipment endpoints. All workers share one encrypted cached token, while a separate invoice importer receives a different client rather than reusing the shipment credential.

## Error Handling

| Failure | Response |
| --- | --- |
| Token request rejected | Check audience, grant type, client identity, and secret source; do not loop. |
| Daily token budget threatened | Stop per-request acquisition and repair shared caching/single-flight behavior. |
| Required endpoint missing | Create a new scoped credential; do not silently substitute a broad key. |
| Secret disclosed | Revoke or rotate immediately and scrub derived logs or artifacts. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Using API credentials](https://developers.flexport.com/tutorials/using-api-credentials/)
- [API credential FAQ](https://developers.flexport.com/faq/api-credentials/)
- [Flexport API reference](https://apidocs.flexport.com/v3/)
