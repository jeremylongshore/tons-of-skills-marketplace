---
name: brightdata-deploy-integration
description: 'Design and review a bounded Bright Data worker deployment with separate proxy, Browser API, scraper, snapshot, and delivery responsibilities. Use when preparing a runtime topology or deployment manifest. Trigger with: "deploy this Bright Data worker", "design Bright Data queues", "review the Bright Data deployment".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: "[deployment-path]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- web-data
- bright-data
- deploy-integration
- operations
compatibility: 'Requires an approved Bright Data workload, managed secrets, queueing, and a deployment platform'
---
# Bright Data Worker Deployment

## Overview

Deploy collection as bounded workers instead of one privileged process. Separate synchronous proxy or Browser API requests from scraper triggers, snapshot polling, downloads, and destination delivery so each stage has its own authority, queue, resource ceiling, and rollback.

## Prerequisites

- An approved workload manifest naming targets, fields, products, and destinations
- Managed secret references and environment-specific Bright Data resources
- Queue, object-storage, quarantine, and observability facilities

## Instructions

### Step 1: Inventory runtime responsibilities

Read the application and Grep for proxy requests, Browser API sessions, `/datasets/v3/trigger`, progress checks, snapshot downloads, and delivery calls. Assign each responsibility to the smallest worker role.

### Step 2: Define admission and isolation

Write or Edit deployment manifests with separate queues and identities for request, browser, trigger, poll, download, validate, and delivery workers. Add target allowlists, byte and record ceilings, timeouts, concurrency bounds, and dead-letter routing.

### Step 3: Protect data movement

Stream large snapshots to bounded storage, validate schema before downstream use, quarantine unexpected content, and require an approved destination before invoking `/datasets/v3/deliver/SNAPSHOT_ID`.

### Step 4: Make rollout reversible

Specify health signals, queue-depth and error-class alerts, canary capacity, drain behavior, rollback version, secret revocation, and replay rules. Produce manifests and a deployment plan; do not initiate production traffic from this skill.

## Tool Discipline

Use Read and Grep for topology and configuration discovery. Use Write and Edit for deployment manifests, queue contracts, policies, tests, and runbooks. This skill does not deploy, rotate credentials, create zones, or send provider requests.

## Output

- Worker and queue topology with explicit trust boundaries
- Resource, data, and destination controls per stage
- Canary, drain, rollback, quarantine, and replay plan

## Examples

A trigger worker creates one approved scraper job, a poller records state transitions, a downloader streams the completed snapshot to quarantine, a validator enforces the schema, and a delivery worker releases only accepted records to an approved destination.

## Error Handling

| Failure | Meaning | Response |
|---------|---------|----------|
| One worker holds every credential | Blast radius is too large | Split identities and secret scopes |
| Download memory grows with snapshot size | Transfer is unbounded | Stream with byte ceilings and backpressure |
| Delivery destination is runtime input | Exfiltration boundary is open | Resolve destinations from an approved manifest |

## Resources

- [Asynchronous scraper requests](https://docs.brightdata.com/api-reference/rest-api/scraper/asynchronous-requests)
- [Download snapshot](https://docs.brightdata.com/api-reference/scrapers/delivery-apis/download-snapshot)
- [Deliver snapshot](https://docs.brightdata.com/api-reference/scrapers/delivery-apis/deliver-snapshot)
- [REST API authentication](https://docs.brightdata.com/api-reference/authentication)
