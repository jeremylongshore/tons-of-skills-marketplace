---
name: quicknode-hello-world
description: 'Prove a new QuickNode RPC endpoint with a minimal, read-only JSON-RPC contract before application integration. Use when onboarding a chain endpoint or separating provider failures from client-library failures. Trigger with: "test my QuickNode endpoint", "make the first QuickNode request", "verify QuickNode RPC".'
allowed-tools: Read, Grep, Write, Edit, Bash(curl:*)
version: 2.0.0
argument-hint: '[chain-and-network]'
model: inherit
effort: medium
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - quicknode
  - blockchain
  - json-rpc
  - verification
compatibility: 'Requires a QuickNode HTTP endpoint and a documented read method for the selected chain'
---

# QuickNode Read-Only Endpoint Proof

## Overview

Establish transport, authentication, chain identity, response shape, and tip movement with raw JSON-RPC before adding an SDK. This keeps the first proof deterministic and prevents a client-library configuration error from looking like an endpoint outage.

## Prerequisites

- A secret reference for the QuickNode endpoint and token
- The expected chain, network, protocol, and chain identifier
- A non-sensitive read method supported by that chain

## Instructions

### Step 1: Inspect the integration

Use Read and Grep to find the endpoint variable, expected chain ID, timeout, and current client wrapper. Stop if source or logs contain a literal QuickNode token.

### Step 2: Define the probe

Use Write or Edit to create a small fixture containing only JSON-RPC version, a read method, empty parameters when valid, and a stable request ID. For EVM, pair `eth_chainId` with `eth_blockNumber`; do not submit a transaction.

### Step 3: Call through the secret boundary

Use Bash(curl:*) with a timeout, JSON content type, and the endpoint injected by the runtime. Suppress verbose output because the URL may contain a token.

```bash
curl --silent --show-error --max-time 10 \
  --header 'content-type: application/json' \
  --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' \
  "$QUICKNODE_ENDPOINT"
```

### Step 4: Validate semantics

Require HTTP success, matching JSON-RPC `id`, exactly one of `result` or `error`, and the expected chain ID. Parse hexadecimal block numbers explicitly rather than comparing their strings.

### Step 5: Prove liveness

Read the latest block twice with a chain-appropriate interval. Tip movement is useful evidence but is not universal during quiet or halted networks, so compare against the chain status before declaring failure.

### Step 6: Capture a safe receipt

Record timestamp, chain, network, method, latency, HTTP status, JSON-RPC error code if any, and redacted endpoint identity. Never retain the endpoint URL.

## Tool Discipline

Use Read and Grep for configuration discovery, Write and Edit for a non-secret probe fixture, and Bash(curl:*) for bounded reads. Do not use this workflow for writes, signing, or funded keys.

## Output

- Endpoint contract and expected chain identity
- Redacted transport and JSON-RPC receipt
- Liveness result with chain-status context
- Clear owner for any failed layer

## Examples

An Ethereum mainnet endpoint returns chain ID `0x1` and a valid block number. A response from a testnet is rejected even though transport and authentication succeeded.

## Error Handling

| Failure | Response |
| --- | --- |
| HTTP 401 or 403 | Check token type, security filters, and secret injection |
| JSON-RPC error | Preserve code and message after redaction; do not flatten it to HTTP |
| Wrong chain ID | Stop deployment and correct endpoint selection |
| Timeout | Compare provider status and a second bounded read before escalation |

## Resources

- [Endpoint-proof evidence and source notes](references/official-docs.md)
- [Ethereum quickstart](https://www.quicknode.com/docs/ethereum/quickstart)
- [QuickNode APIs](https://www.quicknode.com/docs/build-with-ai/quicknode-apis)
