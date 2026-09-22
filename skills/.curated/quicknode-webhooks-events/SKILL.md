---
name: quicknode-webhooks-events
description: 'Build an authenticated, idempotent QuickNode Webhooks or Streams receiver with bounded acknowledgement, replay safety, and reorganization handling. Use when delivering onchain events to HTTP or durable destinations. Trigger with: "receive QuickNode webhooks", "secure a QuickNode Stream", "handle duplicate blockchain events".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[product-dataset-and-destination]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - quicknode
  - webhooks
  - streams
  - events
compatibility: 'Webhooks and Streams have distinct APIs and delivery controls; destination options depend on plan'
---

# QuickNode Event Delivery Contract

## Overview

Choose Webhooks for template-driven notifications or Streams for programmable, historical, and multi-destination pipelines. Both require authenticity, fast acknowledgement, idempotency, and explicit chain-reorganization behavior.

## Prerequisites

- Product choice, chain, network, dataset, and start range
- An HTTPS receiver or approved durable destination
- A secret store, queue, and replay-aware event identity

## Authentication

Authenticate event delivery with the generated HMAC security token and verify the signature over the unmodified request bytes before parsing. For Streams, add mTLS when its trust model is required. Keep endpoint tokens and Admin API keys out of receiver configuration because they authenticate different QuickNode surfaces.

## Instructions

### Step 1: Select Webhooks or Streams

Use Read and Grep to identify filtering, backfill, batching, destination, and reorg needs. Streams supports filter functions and destinations such as webhook, object storage, PostgreSQL, and Kafka; do not paste a Webhooks payload assumption into Streams.

### Step 2: Define authenticity

Use the product's generated security token for HMAC verification. Compare signatures in constant time over the exact received bytes. For Streams, consider mTLS and a private-CA configuration where appropriate.

### Step 3: Bound the receiver

Use Write or Edit to cap body size, decode gzip only when configured, validate content type, verify authenticity before parsing, enqueue durably, and return 2xx within the configured timeout.

### Step 4: Create an idempotency identity

Derive a stable key from product metadata plus chain, block hash, transaction or log position, and destination. Persist receipt before acknowledging; do not deduplicate only by transaction hash when multiple logs are possible.

### Step 5: Handle retries and pauses

Treat delivery as at-least-once at the receiver. Streams processes batches sequentially, retries according to configuration, and can pause after maximum failures. Multiple destinations can replay to ones that already succeeded.

### Step 6: Reconcile reorganizations

Configure and test the product's reorg behavior. Make downstream state reversible or versioned and keep a cursor that can be replayed from a documented block.

## Tool Discipline

Use Read and Grep for receiver discovery and Write/Edit for verification, queueing, idempotency, and tests. Do not create or mutate a production Stream/Webhook without an explicit checkpoint.

## Output

- Product and destination decision
- Authenticated bounded receiver
- Durable idempotency and replay contract
- Retry, pause, reorg, and recovery runbook

## Examples

A Stream receiver verifies HMAC over raw bytes, writes the batch and identity to a queue transactionally, returns 204, and processes business effects asynchronously. A redelivered batch is acknowledged without duplicating effects.

## Error Handling

| Failure | Response |
| --- | --- |
| Signature fails | Reject before parsing and retain only sanitized metadata |
| Receiver exceeds timeout | Move work behind the durable acknowledgement boundary |
| Stream pauses | Repair the failing destination, then replay from the recorded cursor |
| Reorg invalidates an event | Apply the compensating state transition by block identity |

## Resources

- [Delivery evidence and source notes](references/official-docs.md)
- [Streams destinations](https://www.quicknode.com/docs/streams/destinations)
- [Webhooks](https://www.quicknode.com/docs/webhooks)
