---
name: vastai-observability
description: >-
  Observe Vast.ai renter instances and Serverless resources using actionable state, logs, queue, utilization, balance, and cost signals. Use when building dashboards, alerts, or release telemetry. Trigger with: "monitor Vast.ai", "alert on Vast.ai instances", "observe Vast.ai Serverless".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[resource-scope-slos-and-alert-destinations]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - observability
  - alerts
  - serverless
compatibility: 'Requires read-scoped Vast.ai access, resource labels, durable telemetry storage, and named responders.'
---

# Vast.ai Control-Plane Observability

## Overview

Measure provider state and workload health separately. Alerts must identify a resource, threshold, evidence link, responder, and safe action; a dashboard without terminal-state and billing coverage is incomplete.

## Prerequisites

- Instance, endpoint, workergroup, deployment, and account scopes
- Latency, error, queue, utilization, state-age, balance, and cost objectives
- Collection interval, retention, alert routing, and incident owner

## Instructions

### Step 1: Inventory labeled resources

Map instance labels and Serverless IDs to service, environment, release, cost center, and owner.

### Step 2: Collect structured control state

Read instance actual status, timestamps, price, disk, and endpoints; collect endpoint/workergroup status, logs, and deployment versions.

### Step 3: Collect workload signals

Measure request/job success, latency, queue time, GPU utilization, memory, disk, checkpoint age, and last successful artifact.

### Step 4: Add billing protection

Track credit balance, instance and storage charges, active/stopped age, and orphaned resources. Alert before balance or cleanup risk becomes urgent.

### Step 5: Define stateful alerts

Alert on terminal states, excessive transition age, queue/SLO breach, checkpoint staleness, low balance, and cleanup failure with deduplication.

### Step 6: Test the path

Inject a canary event or threshold breach, verify delivery and ownership, then record recovery and false-positive behavior.

## Authentication

Use read-only keys for collectors and distinct secrets for alert sinks. Never put a mutation-capable Vast.ai key in dashboards or telemetry processors.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Resource-to-owner inventory and telemetry schema
- Dashboard and actionable alert definitions
- Alert-path test, retention, and unresolved coverage receipt

Return resource scope, collection interval, SLOs, tested alert, responder, evidence location, and blind spots.

## Examples

A dashboard separates an instance's `running` state from workload request success, pages on stale external checkpoints and low balance, and assigns stopped-storage leaks to the billing owner.

## Error Handling

| Failure | Response |
| --- | --- |
| Collector receives 403 | Add only the documented read category needed by that metric. |
| Resource is missing from inventory | Quarantine the alert and assign ownership before automated action. |
| Metrics lag exceeds the SLO | Mark the dashboard stale and use direct provider state during incidents. |
| Alert contains a secret or payload | Disable the route, scrub data, rotate credentials, and narrow fields. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Serverless logging](https://docs.vast.ai/guides/serverless/logging)
- [Manage instances](https://docs.vast.ai/guides/instances/manage-instances)
- [Notification webhooks](https://docs.vast.ai/guides/reference/notification-webhooks)
