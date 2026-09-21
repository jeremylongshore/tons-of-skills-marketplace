---
name: brightdata-webhooks-events
description: 'Build a secure receiver and replay contract for Bright Data snapshot delivery without assuming provider IPs, payload size, or retry timing. Use when accepting webhook-style dataset delivery. Trigger with: "receive a Bright Data snapshot", "secure Bright Data delivery", "design Bright Data webhook handling".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: "[receiver-path]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- web-data
- bright-data
- snapshot-delivery
- operations
compatibility: 'Requires a managed HTTPS destination, an approved Bright Data snapshot, and durable streaming storage'
---
# Bright Data Snapshot Delivery Receiver

## Overview

Treat snapshot delivery as an untrusted, repeatable data-transfer event. Configure delivery with the current `POST /datasets/v3/deliver/SNAPSHOT_ID` API, authenticate the managed destination, stream the body, validate it, and make downstream processing idempotent.

## Prerequisites

- A completed approved snapshot and its expected schema
- A managed HTTPS endpoint with destination authentication
- Durable quarantine storage and a replay ledger

## Instructions

### Step 1: Establish the delivery contract

Read the receiver and Grep for body buffering, unauthenticated routes, hard-coded provider IPs, guessed retry schedules, and direct writes to trusted tables. Record the expected schema, format, destination, and ownership.

### Step 2: Configure an approved destination

Write or Edit the integration so an authorized control-plane client requests `POST /datasets/v3/deliver/SNAPSHOT_ID` with `type=webhook` and managed destination authentication. Never place destination credentials in the URL or logs.

### Step 3: Receive defensively

Stream the request into bounded quarantine storage. Authenticate before processing, cap bytes and duration, compute a digest, validate format and schema, and derive an idempotency key from trusted delivery context plus content digest.

### Step 4: Acknowledge and replay safely

Acknowledge only after durable acceptance. Make duplicates no-ops, quarantine malformed or oversized content, and replay from retained evidence through the same validator. Do not invent provider retry or source-IP guarantees.

## Tool Discipline

Use Read and Grep to inspect receiver, routing, and storage code. Use Write and Edit for receiver logic, validation, idempotency, fixtures, and the replay runbook. This skill does not invoke delivery or expose a public endpoint.

## Output

- Authenticated streaming receiver contract
- Schema, idempotency, quarantine, and replay implementation
- Redaction-safe success and failure tests

## Examples

The receiver authenticates a managed header, streams NDJSON to quarantine while hashing it, rejects an unexpected schema, and promotes a validated object exactly once even if the same payload arrives again.

## Error Handling

| Failure | Meaning | Response |
|---------|---------|----------|
| Destination auth is missing | Anyone may submit data | Reject before reading the payload |
| Payload exceeds the configured ceiling | Transfer is outside the workload contract | Stop streaming and quarantine metadata |
| Digest already exists | Delivery is a duplicate | Return the documented safe acknowledgement without reprocessing |

## Resources

- [Deliver snapshot](https://docs.brightdata.com/api-reference/scrapers/delivery-apis/deliver-snapshot)
- [Scraper data delivery](https://docs.brightdata.com/products/scrapers/scrapers-library/data-delivery)
- [Download snapshot](https://docs.brightdata.com/api-reference/scrapers/delivery-apis/download-snapshot)
- [REST API authentication](https://docs.brightdata.com/api-reference/authentication)
