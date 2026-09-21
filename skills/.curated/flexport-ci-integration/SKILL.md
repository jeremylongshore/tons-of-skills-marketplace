---
name: flexport-ci-integration
description: >-
  Gate Flexport integrations in CI with credential-free contract tests and an optional protected read-only smoke lane. Use when adding REST, MCP, webhook, version, or mutation safety checks. Trigger with: "test Flexport in CI", "Flexport contract tests", "secure Flexport CI".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[repository-and-surfaces]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - ci
  - testing
compatibility: 'Requires a CI system with fork-secret isolation, sanitized fixtures, and optional protected environment credentials.'
---

# Fork-Safe Flexport Contract CI

## Overview

The required CI lane must run without Flexport secrets and remain safe for forks. Live verification belongs in a protected, non-fork, read-only lane with explicit environment approval.

## Prerequisites

- Sanitized REST, MCP, OAuth-error, and webhook fixtures
- CI permissions model and fork-event policy
- Optional test credential approved through Flexport/account ownership

## Instructions

### Step 1: Build the required lane

Validate schemas, tolerant additive fields, pagination, error classification, webhook raw-body signatures, and mutation guards entirely from fixtures.

### Step 2: Test secret absence

Assert default tests cannot resolve Flexport credentials or reach live mutation adapters.

### Step 3: Protect fork execution

Never expose repository/environment secrets to untrusted pull-request code; keep required fork checks credential-free.

### Step 4: Define an optional live lane

Run only from trusted refs after environment approval, inject a scoped credential, and permit one documented read-only proof.

### Step 5: Block mutations

Enforce an adapter-level CI policy that rejects booking, document, invoice, or purchase-order writes even when a credential exists.

### Step 6: Publish receipts

Attach test counts, fixture/source dates, release SHA, and redacted live outcome; never upload tokens or provider payloads.

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

Every pull request tests v3 shipment envelopes, MCP cursor handling, malformed webhook signatures, and ambiguous booking guards. A protected main-branch job may perform one shipment list read with a test credential.

## Error Handling

| Failure | Response |
| --- | --- |
| Fork can read a secret | Disable the lane and repair event/environment permissions immediately. |
| Fixture contains production data | Replace and purge it before rerunning. |
| Live job can mutate | Fail the policy gate and remove write-capable paths. |
| Schema drift appears | Update from current first-party docs and add a regression fixture. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Flexport v3 API reference](https://apidocs.flexport.com/v3/)
- [MCP tools](https://apidocs.flexport.com/v3/tag/MCP-Tools/)
- [Webhook endpoints](https://apidocs.flexport.com/v3/tag/Webhook-Endpoints/)
