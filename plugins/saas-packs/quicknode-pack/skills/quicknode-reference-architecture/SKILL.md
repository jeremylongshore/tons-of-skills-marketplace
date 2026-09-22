---
name: quicknode-reference-architecture
description: 'Analyze and design a QuickNode production boundary that separates control-plane API keys, data-plane endpoint tokens, chain reads and writes, event ingestion, durable state, and observability. Use when multiple services or QuickNode products need clear ownership and failure isolation. Trigger with: "analyze QuickNode architecture", "design QuickNode infrastructure", "audit QuickNode trust boundaries".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[systems-and-chain-workloads]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - quicknode
  - architecture
  - blockchain
  - governance
compatibility: 'Product availability, destination counts, and endpoint capabilities depend on chain and plan'
---

# QuickNode Production Reference Architecture

## Overview

Separate provisioning and account governance from chain traffic, and separate synchronous reads/writes from asynchronous event ingestion. Give every credential, endpoint, cursor, queue, and recovery path one owner.

## Prerequisites

- Service inventory and trust boundaries
- Chain/network, method, history, write, and event requirements
- SLO, recovery, compliance, and cost constraints

## Instructions

### Step 1: Map control and data planes

Use Read and Grep to identify Admin API, unified SDK, `qn`, RPC/WSS endpoints, Streams, Webhooks, SQL Explorer, and KV Store usage. Mark credentials and mutation authority.

### Step 2: Isolate credentials

Use separate API keys for control-plane automation and endpoint tokens for data-plane RPC. Separate applications and environments with multiple tokens; keep signing keys outside QuickNode clients.

### Step 3: Split synchronous workloads

Route bounded reads through chain-specific adapters. Put transaction intent, signing, broadcast identity, confirmation, and reorg reconciliation behind a dedicated write service.

### Step 4: Build asynchronous ingestion

Terminate Streams or Webhooks at an authenticated receiver, acknowledge after durable enqueue, and process idempotently. Persist a replay cursor and send large historical pipelines to an appropriate durable destination.

### Step 5: Define data capability

Use Write or Edit to record chain, network, API family, add-ons, archive/pruning semantics, pagination, and block consistency. Do not assume feature parity across chains.

### Step 6: Close observability and recovery

Correlate application requests with endpoint metrics and sanitized request IDs. Define endpoint/token cutover, chain-provider degradation, event replay, transaction reconciliation, and budget alerts.

## Tool Discipline

Use Read and Grep for topology discovery and Write/Edit for architecture records, interfaces, and tests. This design workflow performs no account, endpoint, Stream, or production mutation.

## Output

- Trust-boundary and credential map
- Synchronous read/write interfaces
- Durable event-ingestion and replay path
- Observability, cost, and recovery contracts

## Examples

An API serves cached finalized reads, a signer service owns transaction state, and a Stream receiver writes authenticated batches to a queue. Admin automation has no signer or endpoint token.

## Error Handling

| Failure | Response |
| --- | --- |
| One key spans control and data planes | Split identity and rotate through overlap |
| Event receiver performs business work inline | Insert a durable queue before acknowledgement |
| Chain capability is assumed | Bind the interface to a verified chain/network contract |
| Provider timeout can duplicate a write | Persist broadcast identity and reconcile before retry |

## Resources

- [Architecture evidence and source notes](references/official-docs.md)
- [QuickNode APIs](https://www.quicknode.com/docs/build-with-ai/quicknode-apis)
- [Streams destinations](https://www.quicknode.com/docs/streams/destinations)
