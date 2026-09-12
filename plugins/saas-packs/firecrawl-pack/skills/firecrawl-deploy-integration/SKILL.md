---
name: firecrawl-deploy-integration
description: >-
  Deploy a Firecrawl v2 client integration or a reviewed self-hosted stack with secrets, canaries, health evidence, and rollback controls. Use when releasing Firecrawl-backed services. Trigger with "deploy Firecrawl", "Firecrawl production rollout", or "self-host Firecrawl".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <environment>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, deployment, operations]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Production Deployment

## Overview

Deploy the application client and the Firecrawl service as separate responsibilities. Cloud integrations need a protected key and egress policy; self-hosting adds databases, queues, browsers, storage, authentication, upgrades, and recovery.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Cloud clients use the v2 API and secret-managed FIRECRAWL_API_KEY. The official self-host guide's Compose example is an evaluation baseline with authentication disabled and without durable storage, TLS, high availability, or every Cloud capability. Pin the reviewed release and its own Compose contract; do not copy a floating main configuration into production.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Inventory the application release, Firecrawl Cloud or self-host decision, required features, environments, domains, data flows, SLOs, and rollback owner.
2. For Cloud, inject the key from the platform secret manager, restrict outbound destinations, choose retention/cache policy, and prevent request or response bodies from application logs.
3. For self-hosting, pin a verified release and review its Compose, SELF_HOST, and feature-support documentation. Map every optional provider and outbound flow.
4. Before exposure, add supported authentication, network controls, TLS, durable PostgreSQL/Redis/RabbitMQ storage where required, backups, restore tests, monitoring, capacity limits, and upgrade rollback.
5. Deploy a no-traffic revision, verify process readiness separately from one approved functional v2 scrape, then run a bounded content-free canary.
6. Observe errors, queue pressure, latency, credit or capacity use, and output-quality metrics. Promote gradually with explicit stop thresholds.
7. Record the release/image digest, configuration hashes, canary evidence, approvals, and rollback result.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before exposing a self-hosted API, disabling authentication, adding external AI/proxy providers, granting production secrets, changing retention, or increasing rollout traffic.

## Output

Return deployment topology, immutable versions, secret and network controls, storage/recovery posture, capability gaps, readiness and functional canary results, rollout state, and tested rollback command or procedure.

## Error Handling

- Readiness passes but scrape fails: inspect API and browser-service evidence; do not declare the deployment healthy.
- Self-hosted capability is absent: stop and choose Cloud or validate its external dependency.
- Rollback cannot restore data/configuration: block production promotion.

## Examples

- "Deploy our Firecrawl client" produces a secret-managed canary rollout and rollback receipt.
- "Expose the quickstart Compose file publicly" is blocked until production authentication, TLS, storage, and recovery exist.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
