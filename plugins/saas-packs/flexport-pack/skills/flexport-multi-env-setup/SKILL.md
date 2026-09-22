---
name: flexport-multi-env-setup
description: >-
  Separate Flexport development, test, staging, and production configuration without inventing provider hostnames or key prefixes. Use when creating environments, test credentials, receivers, or promotion rules. Trigger with: "Flexport environments", "Flexport staging setup", "separate Flexport credentials".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[environment-matrix]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - environments
  - configuration
compatibility: 'Requires environment owners, separate secret stores, and Flexport/account-executive coordination for any test credential.'
---

# Flexport Environment and Credential Isolation

## Overview

Flexport documents the same API base rather than arbitrary environment URLs. Isolation comes from accounts/credentials, receiver URLs, data policy, and mutation gates; a test credential may require coordination with the account executive.

## Prerequisites

- Environment/account matrix and data classification
- Distinct credential aliases and secret-store namespaces
- Separate webhook URLs, queues, databases, and mutation policy

## Instructions

### Step 1: Define each boundary

For every environment record account identity, credential type, endpoint resources, version behavior, receiver, data class, and permitted operations.

### Step 2: Issue distinct credentials

Never share client IDs, client secrets, API keys, cached tokens, or MCP sessions across environments.

### Step 3: Keep canonical hosts

Use documented Flexport API/MCP hosts. Do not invent `staging` subdomains or infer an environment from a credential prefix.

### Step 4: Control test access

Request any Flexport test credential through the documented account-executive route and keep local/default tests fixture-only.

### Step 5: Gate promotion

Promote immutable artifacts while supplying environment-specific secret references and config. Production mutations remain disabled until canary approval.

### Step 6: Prove non-crossing

Test that each environment rejects another's credential alias, callback destination, queue, and data-store identity.

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

Staging and production run the same artifact against documented hosts, but use different credential records, callback URLs, queues, stores, and mutation flags. Default developer tests use no live Flexport credential.

## Error Handling

| Failure | Response |
| --- | --- |
| Credential reused across environments | Rotate or separate it before promotion. |
| Undocumented environment host configured | Remove it and verify the official account/credential model. |
| Production data enters test | Contain and delete under policy, then repair routing controls. |
| Test credential unavailable | Use sanitized fixtures; do not borrow production access. |

## Resources

- [First-party source notes](references/official-docs.md)
- [API credential FAQ](https://developers.flexport.com/faq/api-credentials/)
- [Using API credentials](https://developers.flexport.com/tutorials/using-api-credentials/)
- [Flexport v3 API reference](https://apidocs.flexport.com/v3/)
