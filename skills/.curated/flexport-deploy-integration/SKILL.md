---
name: flexport-deploy-integration
description: >-
  Deploy a Flexport REST, MCP, or webhook integration through provider-neutral canaries and rollback gates. Use when releasing credential, receiver, schema, or workflow changes. Trigger with: "deploy Flexport integration", "canary Flexport webhook", "roll back Flexport release".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[release-sha-and-surface]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - deployment
  - reliability
compatibility: 'Requires an approved delivery platform, secret injection, health checks, and rollback capability.'
---

# Flexport Integration Deployment Canary

## Overview

Keep deployment mechanics provider-neutral and Flexport validation surface-specific. A safe release proves secret injection, read-only access, version handling, webhook raw-body verification, and mutation gates before traffic expands.

## Prerequisites

- Immutable release artifact and reviewed configuration diff
- Secret references supplied by the deployment platform, not command-line values
- Read-only canary and tested rollback procedure

## Instructions

### Step 1: Classify the change

Label REST schema/version, OAuth credential, MCP tool/session, webhook receiver, or business-policy change and name its rollback unit.

### Step 2: Validate offline

Run contract fixtures for documented success, additive fields, auth errors, webhook signatures, and ambiguous mutations.

### Step 3: Deploy dark

Start the release with mutations disabled and no automatic booking, document creation, or record update.

### Step 4: Run a read-only canary

Reuse a cached token and perform one approved shipment read or MCP tracking call. For receivers, send a signed synthetic fixture through the exact raw-body path.

### Step 5: Expand gradually

Increase traffic by a reversible cohort while monitoring auth, permission, parsing, queue, duplicate, and reconciliation outcomes.

### Step 6: Rollback on invariant breach

Restore the prior artifact/configuration together, preserve redacted evidence, and reconcile any ambiguous in-flight mutation.

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

A receiver release first validates a synthetic `X-Hub-Signature-256` request, then receives a small traffic cohort. Any authentication or duplicate-rate regression routes callbacks back to the previous release.

## Error Handling

| Failure | Response |
| --- | --- |
| Secret absent | Fail startup; never accept an unauthenticated fallback. |
| Canary uses wrong account/version | Stop rollout and correct configuration identity. |
| Mutation occurs in dark mode | Disable the release and reconcile the resource immediately. |
| Rollback leaves queue split | Pause consumers and restore one authoritative ownership boundary. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Versioning](https://apidocs.flexport.com/v3/tag/Versioning/)
- [Webhook endpoints](https://apidocs.flexport.com/v3/tag/Webhook-Endpoints/)
- [MCP tools](https://apidocs.flexport.com/v3/tag/MCP-Tools/)
