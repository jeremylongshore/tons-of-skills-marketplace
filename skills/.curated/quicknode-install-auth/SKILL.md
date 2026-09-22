---
name: quicknode-install-auth
description: 'Choose and configure the correct QuickNode credential boundary for RPC endpoints, the Admin API, the unified SDK, and the qn CLI. Use when onboarding an endpoint, separating environments, or rotating access without exposing tokens. Trigger with: "authenticate QuickNode", "configure a QuickNode endpoint", "rotate QuickNode credentials".'
allowed-tools: Read, Grep, Write, Edit, Bash(qn:*), Bash(curl:*)
version: 2.0.0
argument-hint: '[client-and-environment-scope]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - quicknode
  - blockchain
  - authentication
  - secrets
compatibility: 'Requires a QuickNode account; Admin API and advanced endpoint-security features depend on the account plan'
---

# QuickNode Credential Boundary

## Overview

Separate data-plane endpoint tokens from account-level API keys. An endpoint token authorizes chain RPC traffic; an API key authorizes QuickNode product and control-plane clients such as Admin API, Streams, the unified SDK, and `qn`.

## Prerequisites

- The client, chain, network, environment, and required QuickNode products
- An approved secret manager and named rotation owner
- A QuickNode account role permitted to create only the required credential

## Instructions

### Step 1: Inventory credential consumers

Use Read and Grep to locate endpoint URLs, `x-token`, `x-api-key`, `QN_SDK__API_KEY`, and `QUICKNODE_*` references. Record owners without printing values. Treat any token embedded in an RPC URL as secret material.

### Step 2: Select the credential type

Use an endpoint authentication token for HTTP or WSS chain RPC. Prefer the `x-token` header for server-side clients when the chain endpoint supports it. Use a dashboard API key for Admin API, SDK, Streams, Webhooks, KV Store, or SQL Explorer access.

### Step 3: Separate environments

Give development, staging, production, and independent applications separate endpoint tokens. Multi-token authentication permits revoking one consumer without rotating every workload. Do not reuse a human CLI session as a production service identity.

### Step 4: Configure clients safely

Use Write or Edit to add secret references and documented variable names, never values. Configure the unified SDK with `QN_SDK__API_KEY`. Use Bash(qn:*) for `qn auth login` and `qn auth whoami` only in an approved interactive operator session.

### Step 5: Verify the intended boundary

Use Bash(curl:*) for one read-only JSON-RPC probe with the token supplied by the runtime secret mechanism. Confirm the chain identifier and an expected denial after removing the credential; never echo the endpoint URL or request headers.

### Step 6: Record rotation

Document credential type, endpoint or API scope, consumers, storage reference, creation date, review date, and revoke-first rollback. Rotate with overlap: create, deploy, verify, then revoke the old token.

## Tool Discipline

Use Read and Grep for discovery, Write and Edit for secret references, Bash(qn:*) for authenticated CLI identity checks, and Bash(curl:*) only for redacted read probes. Never place a live endpoint URL in source, logs, shell history, or support evidence.

## Output

- Credential-to-client matrix
- Environment-separated secret references
- Negative and positive verification results
- Rotation and revocation record

## Examples

A production RPC service receives a dedicated endpoint token through its secret manager. A deployment auditor uses a separate `x-api-key` identity through the SDK and cannot submit chain transactions.

## Error Handling

| Failure | Response |
| --- | --- |
| Endpoint returns unauthorized | Verify endpoint token placement without logging it |
| Admin API returns 401 | Verify the API key and account scope, not the RPC token |
| Token appears in a URL log | Revoke it, sanitize retained logs, and replace it |
| Rotation breaks one consumer | Restore the old secret reference during the overlap window |

## Resources

- [Authentication evidence and source notes](references/official-docs.md)
- [QuickNode SDK quickstart](https://www.quicknode.com/docs/sdk/quick-start)
- [Multi-token authentication](https://www.quicknode.com/guides/quicknode-products/endpoint-security/how-to-set-up-multi-token-authentication-on-quicknode)
