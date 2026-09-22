---
name: quicknode-deploy-integration
description: 'Deploy a QuickNode integration with environment-scoped endpoints, preflight reads, staged traffic, observability, and reversible credential cutover. Use when releasing a new RPC endpoint, SDK client, Stream, or Webhook consumer. Trigger with: "deploy QuickNode", "roll out a QuickNode endpoint", "canary a QuickNode integration".'
allowed-tools: Read, Grep, Write, Edit, Bash(qn:*)
version: 2.0.0
argument-hint: '[environment-and-release-id]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - quicknode
  - deployment
  - canary
  - rollback
compatibility: 'Control-plane reads require authenticated qn access; product and endpoint changes remain approval-gated'
---

# QuickNode Deployment Gate

## Overview

Release configuration before traffic, prove the selected chain and product contracts, then increase exposure in stages. Keep old endpoints or tokens available through a bounded rollback window.

## Prerequisites

- Release commit, target environment, endpoint and product inventory
- Secret-manager references for environment-specific credentials
- SLO, canary cohort, rollback owner, and maximum cutover window

## Instructions

### Step 1: Audit the release

Use Read and Grep to find endpoint variables, literal URLs, chain IDs, network names, SDK versions, write paths, Stream/Webhook destinations, and timeout/retry changes.

### Step 2: Validate control-plane state

Use Bash(qn:*) for read-only endpoint, Stream, Webhook, security, usage, and metrics inspection. Confirm target resources exist and are active without changing status.

### Step 3: Render safe configuration

Use Write or Edit to bind environment-specific secret references, expected chain identity, finite timeouts, bounded concurrency, and feature flags. Keep endpoint tokens out of artifacts and client bundles.

### Step 4: Run preflight

Execute contract tests and one protected read-only request. For event products, use their test or preview path and confirm destination acknowledgement without creating business effects.

### Step 5: Canary traffic

Shift a small declared cohort, then compare latency percentiles, error layers, chain identity, credit use, transaction landing or event completeness, and downstream queue health.

### Step 6: Promote or roll back

Promote only when acceptance thresholds hold for the declared window. Roll back configuration and traffic before revoking the old credential; rotate compromised credentials immediately.

## Tool Discipline

Use Read/Grep for release discovery, Write/Edit for reviewed configuration, and Bash(qn:*) for read-only control-plane evidence. Production mutation and traffic shifts require an explicit operator checkpoint.

## Output

- Release and resource inventory
- Preflight and canary evidence
- Promotion thresholds and decision
- Tested rollback with credential-overlap deadline

## Examples

A new endpoint receives five percent of read traffic. Chain ID, p95 latency, error rate, and credits remain within bounds before the service advances to the next stage.

## Error Handling

| Failure | Response |
| --- | --- |
| Wrong chain or network | Stop before traffic and correct configuration |
| Canary errors exceed threshold | Roll back traffic while retaining evidence |
| Event destination does not acknowledge | Pause rollout and repair the receiver |
| Token leaks in deployment output | Revoke, sanitize, and restart the cutover |

## Resources

- [Deployment evidence and source notes](references/official-docs.md)
- [QuickNode CLI](https://www.quicknode.com/docs/cli)
- [Admin API](https://www.quicknode.com/docs/admin-api)
