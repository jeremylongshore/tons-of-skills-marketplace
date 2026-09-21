---
name: brightdata-reference-architecture
description: 'Create a governed Bright Data collection architecture with separate control, collection, quarantine, validation, and delivery trust zones. Use when designing or reviewing a production topology. Trigger with: "architect a Bright Data system", "draw Bright Data trust boundaries", "review collection architecture".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: "[system-or-design-path]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- web-data
- bright-data
- reference-architecture
- operations
compatibility: 'Requires an approved public-data use case, named system owners, and current Bright Data product documentation'
---
# Bright Data Governed Collection Architecture

## Overview

Design collection as a policy-governed data pipeline, not a direct application call. Separate human approval and configuration from collection workers, then quarantine and validate all results before any trusted consumer or external destination receives them.

## Prerequisites

- Approved purpose, targets, fields, products, retention, recipients, and owners
- Current proxy, Browser API, scraper, snapshot, and delivery requirements
- Platform identity, queue, storage, policy, and observability capabilities

## Instructions

### Step 1: Discover the existing planes

Read design and runtime files and Grep for Bright Data credentials, zones, API endpoints, browser sessions, queues, snapshot storage, and downstream destinations. Mark every trust transition and uncontrolled shortcut.

### Step 2: Define the topology

Write or Edit an architecture with these responsibilities:

```text
Approval + workload registry -> admission controller -> bounded collection workers
                                                   -> quarantine storage
Quarantine -> schema/policy validation -> approved internal consumer
                                    \-> approved snapshot delivery destination
Telemetry <- redacted events, error classes, usage units, and decision receipts
```

Keep proxy and Browser API credentials in worker-specific secret bindings and REST API keys in authorized control-plane identities.

### Step 3: Apply cross-cutting controls

Specify target and destination allowlists, least privilege, environment isolation, job and byte ceilings, backpressure, idempotency, schema validation, retention, deletion, redaction, audit evidence, and independent emergency stop.

### Step 4: Challenge the design

Test policy denial, revoked credentials, 429, provider 5xx, browser timeout, snapshot failure or expiry, schema drift, duplicate delivery, storage exhaustion, and downstream outage. Require an owner and recovery decision for each path.

## Tool Discipline

Use Read and Grep for topology discovery and evidence gathering. Use Write and Edit for diagrams, threat models, contracts, tests, and architecture decisions. This skill does not provision Bright Data resources or initiate collection.

## Output

- Control-plane and data-plane topology with trust boundaries
- Responsibility, secret, data, and destination matrix
- Failure analysis, rollback path, and decision record

## Examples

An admission controller accepts only signed workload manifests. Product-specific workers emit raw results to quarantine, validators release an approved schema, and delivery resolves only named destinations while redacted telemetry preserves an audit trail.

## Error Handling

| Failure | Meaning | Response |
|---------|---------|----------|
| Application code can choose arbitrary targets | Admission boundary is missing | Route requests through the workload registry |
| Raw collection reaches analytics directly | Validation boundary is bypassed | Require quarantine and schema promotion |
| Control and collection share one broad API key | Identity blast radius is excessive | Split identities and scopes |

## Resources

- [REST API authentication](https://docs.brightdata.com/api-reference/authentication)
- [Browser API introduction](https://docs.brightdata.com/products/scraping-browser/introduction)
- [Asynchronous scraper requests](https://docs.brightdata.com/api-reference/rest-api/scraper/asynchronous-requests)
- [Deliver snapshot](https://docs.brightdata.com/api-reference/scrapers/delivery-apis/deliver-snapshot)
