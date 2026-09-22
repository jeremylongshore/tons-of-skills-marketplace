---
name: quicknode-common-errors
description: 'Triage QuickNode transport, authentication, security-filter, capacity, chain, and application failures while preserving the original error layer. Use when RPC, SDK, or endpoint requests fail and ownership is unclear. Trigger with: "debug a QuickNode error", "QuickNode RPC failed", "classify a QuickNode error code".'
allowed-tools: Read, Grep, Bash(qn:*)
version: 2.0.0
argument-hint: '[redacted-error-and-endpoint-id]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - quicknode
  - troubleshooting
  - json-rpc
  - operations
compatibility: 'Error meanings can be chain-specific; use the selected chain reference plus QuickNode infrastructure codes'
---

# QuickNode Error Triage

## Overview

Preserve HTTP status, JSON-RPC code, chain error, method, network, and request identifier as separate facts. Do not treat every `-32000` family response as retryable or overwrite a contract revert with a provider diagnosis.

## Prerequisites

- A redacted failing request and response
- Endpoint ID, chain, network, protocol, and client version
- The expected method contract and a nearby successful request if available

## Instructions

### Step 1: Capture the first failure

Use Read and Grep to locate the earliest complete failure before wrapper retries transform it. Redact endpoint tokens, API keys, signed transactions, addresses when sensitive, and request bodies not needed for diagnosis.

### Step 2: Assign the layer

Classify DNS/TLS/timeout, HTTP authentication, QuickNode infrastructure, endpoint security, chain-node, smart-contract, or client-decoding failure. Keep nested causes intact.

### Step 3: Interpret QuickNode codes

Recognize `-32007` per-second limit, `-32008` per-minute limit, `-32011` method limit, `-32604` empty or unsupported method, and `-32611` endpoint security-filter rejection. Verify other codes against the chain-specific reference.

### Step 4: Inspect control-plane evidence

Use Bash(qn:*) for authenticated endpoint, metrics, or permitted error-log reads. Admin API endpoint logs are plan-gated; absence of access is not proof that no request reached QuickNode.

### Step 5: Run one discriminating test

Compare a supported read method on the same endpoint, the same method with corrected parameters, or the same request in a non-production environment. Avoid retries that could resubmit a signed transaction.

### Step 6: Route ownership

Assign the finding to credential owner, endpoint-security owner, capacity owner, chain integration, contract developer, or QuickNode support. Include only sanitized evidence and a reversible next action.

## Tool Discipline

Use Read and Grep for local evidence and Bash(qn:*) only for read-only account inspection. This diagnostic workflow does not edit code, rotate credentials, change limits, or replay writes.

## Output

- Layered failure classification
- Preserved HTTP, RPC, and chain facts
- One discriminating test result
- Named owner and safe next action

## Examples

HTTP succeeds but JSON-RPC returns `-32611`; a simple allowed method works. Route the issue to endpoint filter configuration instead of increasing capacity or retrying.

## Error Handling

| Signal | Interpretation guardrail |
| --- | --- |
| 401 or 403 | Check credential type and security policy |
| 429 plus RPC code | Preserve both; use the RPC code to identify the limit |
| Contract revert | Decode against ABI and chain state; do not auto-retry |
| Method unsupported | Verify chain, network, add-on, and current method reference |

## Resources

- [Error-triage evidence and source notes](references/official-docs.md)
- [QuickNode error codes](https://www.quicknode.com/docs/cosmos/error-references)
- [Admin API endpoint logs](https://www.quicknode.com/docs/admin-api/logs/v0-endpoints-id-logs)
