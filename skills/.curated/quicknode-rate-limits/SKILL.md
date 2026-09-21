---
name: quicknode-rate-limits
description: 'Analyze and govern QuickNode plan, IP, and method-specific rate limits without inventing a universal threshold. Use when requests receive QuickNode limit codes, one method needs a protective budget, or retry policy must respect endpoint controls. Trigger with: "analyze a QuickNode rate limit", "detect a method limit", "control QuickNode request bursts".'
allowed-tools: Read, Grep, Write, Edit, Bash(qn:*)
version: 2.0.0
argument-hint: '[endpoint-id-and-method]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - quicknode
  - rate-limits
  - reliability
  - operations
compatibility: 'Method and advanced endpoint limits depend on plan and chain; qn access requires an authenticated account'
---

# QuickNode Rate-Limit Control

## Overview

Treat account-plan ceilings, IP limits, and operator-configured method limits as separate controls. QuickNode exposes distinct JSON-RPC errors for per-second, per-minute, and method limits; an HTTP status alone is not sufficient diagnosis.

## Prerequisites

- Endpoint ID, plan, chain, network, and affected method
- A redacted error sample with HTTP and JSON-RPC fields
- Authorized dashboard, Admin API, or `qn` read access

## Authentication

Authenticate `qn` interactively with `qn auth login` and verify the intended account with `qn auth whoami`. For direct Admin API inspection, inject a separate account API key as the `x-api-key` header. Endpoint tokens in URLs or `x-token` headers authenticate RPC traffic but do not replace control-plane credentials.

## Instructions

### Step 1: Classify the signal

Use Read and Grep to find the first complete redacted response. Preserve QuickNode codes such as `-32007` per-second, `-32008` per-minute, and `-32011` method limit. Separate client timeouts and chain-node errors.

### Step 2: Read the configured limits

Use Bash(qn:*) to inspect endpoint and method-rate settings through authenticated read commands. If the CLI version lacks the required view, use the dashboard or documented Admin API rather than guessing a number.

### Step 3: Measure demand

Group requests by endpoint, token, source IP, method, and interval. Distinguish HTTP calls from WebSocket subscription creation; subscription responses do not count like new requests.

### Step 4: Choose the control

Reduce concurrency, coalesce duplicate reads, cache immutable results, or set a method limit that protects expensive calls. Raising a plan limit is a capacity decision, not the first retry strategy.

### Step 5: Implement bounded retry

Use Write or Edit to retry only idempotent reads and only recognized transient limit responses. Apply jitter, cap attempts and elapsed time, and honor a provider delay header when documented. Never automatically replay transaction submissions.

### Step 6: Prove under load

Test below and above the intended threshold in a non-production endpoint. Confirm the expected code, bounded client behavior, recovery, and absence of synchronized retry bursts.

## Tool Discipline

Use Read and Grep for error and demand discovery, Bash(qn:*) for authenticated read-only control-plane inspection, and Write/Edit for bounded retry or throttling code. Require explicit approval before changing production limits.

## Output

- Limit-layer classification
- Measured method and interval demand
- Bounded client-control change
- Before/after load receipt and rollback threshold

## Examples

A single trace method hits `-32011` while ordinary reads succeed. The operator caps that method and queues callers instead of applying a global retry loop to every RPC request.

## Error Handling

| Failure | Response |
| --- | --- |
| `-32007` | Reduce per-second bursts or review plan capacity |
| `-32008` | Flatten longer-window demand and inspect batch jobs |
| `-32011` | Inspect the endpoint's method-specific rule |
| Transaction submission is limited | Reconcile transaction identity before any manual retry |

## Resources

- [Rate-limit evidence and source notes](references/official-docs.md)
- [Method rate limits](https://www.quicknode.com/guides/quicknode-products/endpoint-security/how-to-setup-method-rate-limits)
- [QuickNode error reference](https://www.quicknode.com/docs/cosmos/error-references)
