---
name: quicknode-debug-bundle
description: 'Collect a bounded, redacted QuickNode incident bundle that preserves endpoint, method, timing, HTTP, JSON-RPC, chain, and client evidence without leaking credentials or signed payloads. Use when escalating a reproducible provider or integration failure. Trigger with: "build a QuickNode debug bundle", "collect QuickNode support evidence", "triage an RPC incident".'
allowed-tools: Read, Grep, Bash(qn:*)
version: 2.0.0
argument-hint: '[endpoint-id-and-time-window]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - quicknode
  - debugging
  - incidents
  - support
compatibility: 'Detailed endpoint logs are Enterprise-only; collect equivalent application evidence when unavailable'
---

# QuickNode Redacted Debug Bundle

## Overview

Collect the smallest evidence set that can distinguish transport, QuickNode infrastructure, endpoint policy, chain, and client failures. Never archive a full endpoint URL, API key, endpoint token, private key, or signed raw transaction.

## Prerequisites

- Endpoint ID, chain, network, method, and bounded UTC window
- Incident owner and approved evidence destination
- Redaction rules for addresses, calldata, and business payloads

## Instructions

### Step 1: Freeze scope

State the first and last relevant timestamps, affected deployment, client version, endpoint ID, network, and request class. Exclude unrelated logs and broad home-directory collection.

### Step 2: Gather local evidence

Use Read and Grep for sanitized configuration shape, application error chain, retry count, timeout, request ID, and dependency versions. Replace endpoint URLs with a stable redacted label.

### Step 3: Gather provider evidence

Use Bash(qn:*) for authenticated, read-only endpoint status, metrics, and permitted error logs. Detailed Admin API logs are plan-gated; record “not available” instead of widening access.

### Step 4: Preserve protocol layers

Record DNS/TLS outcome, HTTP status, JSON-RPC `id`, error code and message, chain error, latency, and response size separately. Include one nearby successful method when safe.

### Step 5: Reproduce minimally

Use a documented read method, timeout, and non-production or read-only context. Do not reproduce transaction submission, a contract write, or a historical scan with uncontrolled range.

### Step 6: Run a leak review

Use Grep on the proposed bundle for `quiknode.pro`, token-like paths, `x-token`, `x-api-key`, private-key markers, authorization headers, and raw signed transactions. Refuse delivery until findings are removed.

## Tool Discipline

Use Read and Grep for bounded local evidence and Bash(qn:*) for read-only provider facts. This skill does not write archives, upload files, alter endpoints, or call transaction methods.

## Output

- Scope and UTC incident window
- Redacted layered request/response evidence
- Metrics and provider-status comparison
- Minimal reproduction and leak-review receipt

## Examples

A bundle includes endpoint ID, `eth_getLogs`, a ten-minute window, p95 latency, HTTP 200 with JSON-RPC error, and a sanitized request ID. It excludes the endpoint hostname path and log-filter contents.

## Error Handling

| Failure | Response |
| --- | --- |
| Detailed logs unavailable | Use metrics and application evidence; state the plan boundary |
| Token found in bundle | Stop, revoke if exposed, redact, and rescan |
| Reproduction is destructive | Replace it with a read-only discriminating probe |
| Evidence is too broad | Narrow time, method, endpoint, and deployment |

## Resources

- [Debug-bundle evidence and source notes](references/official-docs.md)
- [Endpoint logs API](https://www.quicknode.com/docs/admin-api/logs/v0-endpoints-id-logs)
- [Endpoint metrics API](https://www.quicknode.com/docs/admin-api/endpoint-metrics/v0-endpoints-id-metrics)
