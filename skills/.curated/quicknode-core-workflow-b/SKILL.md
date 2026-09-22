---
name: quicknode-core-workflow-b
description: 'Analyze and specify a chain-data contract for QuickNode across network identity, API family, historical retention, archive access, pagination, and add-ons. Use when a workload needs historical state, traces, tokens, NFTs, or chain-specific APIs. Trigger with: "analyze QuickNode data requirements", "audit archive access", "design a QuickNode read workload".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[chain-network-and-data-requirement]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - quicknode
  - blockchain
  - archive
  - data-contract
compatibility: 'Supported APIs, archive availability, pruning, and add-ons vary by chain and network'
---

# QuickNode Chain-Data Contract

## Overview

Select an endpoint from required data semantics, not from a generic “Web3 RPC” label. Current state, historical block data, historical state, traces, token/NFT indexes, REST, gRPC, and WebSocket subscriptions have different availability and retention.

## Prerequisites

- Chain, network, and protocol requirements
- Oldest required block, state, or epoch
- Required methods, consistency, pagination, latency, and recovery behavior

## Authentication

Use an endpoint token for data-plane RPC, passed through the documented endpoint URL or `x-token` header. Use a separate account API key in `x-api-key` only for Admin API capability inspection. Never place either credential in the written data contract or its tests.

## Instructions

### Step 1: Inventory queries

Use Read and Grep to extract every RPC, REST, gRPC, subscription, and add-on method. Record block tags, pagination assumptions, expected response shapes, and historical lookback.

### Step 2: Classify historical semantics

Distinguish historical block retrieval from historical state queries. Determine whether the chain exposes archive mode, a pruning window, or a specialized endpoint path. Never infer “archive” from an Ethereum-centric example.

### Step 3: Verify the chain reference

Consult the current QuickNode API overview for the exact chain and network. Confirm supported APIs, protocols, chain ID, archive status, pruning policy, and product availability.

### Step 4: Separate standard and enhanced APIs

Identify standard chain methods versus QuickNode add-ons or indexed Token/NFT APIs. Record entitlement and method contract explicitly; a `qn_*` name does not guarantee it is enabled on every endpoint.

### Step 5: Design bounded reads

Use Write or Edit to add pagination, maximum range, explicit block tags, response-size controls, and checkpointing. Treat a missing next-page token or pruned-state response as a contract event.

### Step 6: Prove representative history

Test current, boundary-age, and oldest-required records in a non-destructive acceptance suite. Pin expected chain identity and response invariants without snapshotting volatile tip values.

## Tool Discipline

Use Read and Grep for query discovery and Write/Edit for the data contract and tests. This design skill does not enable add-ons, provision endpoints, or execute production queries.

## Output

- Chain/network/API capability matrix
- Historical retention and archive decision
- Pagination and checkpoint contract
- Representative acceptance cases and plan dependencies

## Examples

An analytics service needs historical contract state, not merely old block bodies. Its architecture selects an archive-capable network endpoint and tests a block older than the ordinary pruning boundary.

## Error Handling

| Failure | Response |
| --- | --- |
| Historical state unavailable | Recheck archive support and chain pruning policy |
| Method not found | Verify API family, add-on, chain, and endpoint entitlement |
| Page silently truncates | Require and persist the documented continuation token |
| Chain ID differs | Stop and correct the endpoint before consuming data |

## Resources

- [Chain-data evidence and source notes](references/official-docs.md)
- [Supported chains and pruning](https://www.quicknode.com/docs/platform/supported-chains-node-types)
- [Ethereum API overview](https://www.quicknode.com/docs/ethereum/api-overview)
