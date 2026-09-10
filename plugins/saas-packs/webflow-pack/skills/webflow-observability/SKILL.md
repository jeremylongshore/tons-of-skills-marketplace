---
name: webflow-observability
description: >-
  Instrument a Webflow integration around API budgets, errors, cache behavior, webhooks, and deployments without leaking sensitive data. Use when adding metrics, logs, traces, or alerts. Trigger with "monitor Webflow", "Webflow observability", or "Webflow alerts".
argument-hint: "[project-path] [service-or-environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- observability
- monitoring
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow Integration Observability

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- Record HTTP status plus Webflow `code`, `message`, and bounded `details`; do not rely on exception text alone.
- Rate-limit headers and `Retry-After` explain request-budget pressure; Content Delivery adds `cf-cache-status` for cache behavior.
- Webhook registration exposes operational fields such as `lastTriggered`, while delivery health also depends on handler latency and deduplication.
- Webflow Cloud deployment and runtime logs are tied to app, environment, and deployment IDs; successful enqueue is not a deployment success metric.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Define service-level objectives for freshness, successful reads/writes, publish latency, webhook processing, and deployment availability.
2. Instrument request count, latency, status, error code, retry count, endpoint family, environment, and redacted site identity.
3. Track rate headroom and CDN HIT/MISS/BYPASS separately; avoid high-cardinality item IDs and personal data.
4. Measure webhook verification failures, age, duplicates, queue delay, handler duration, and last successful event by trigger.
5. For Cloud apps, correlate build/runtime logs and terminal deployment state with deployment IDs.
6. Add actionable alerts with owner, evidence link, safe first check, and a threshold based on observed baseline.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| Metrics contain payload data | Remove or hash sensitive dimensions and rotate affected telemetry access if needed. |
| Alert has no action | Tie it to a runbook step and verified identity. |
| Success measured at enqueue | Change the signal to terminal state plus public-route verification. |

## Examples

Alert when a verified production token's rate headroom stays low while origin MISS traffic rises, linking the endpoint class and runbook without logging item payloads or bearer headers.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
