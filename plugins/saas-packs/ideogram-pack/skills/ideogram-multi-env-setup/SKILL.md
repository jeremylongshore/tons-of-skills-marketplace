---
name: ideogram-multi-env-setup
description: >-
  Isolate Ideogram development, staging, and production across keys, budgets, webhook routes, storage, data, and promotion evidence. Use when designing or auditing environment separation. Trigger with "separate Ideogram environments", "configure Ideogram staging", or "audit Ideogram promotion".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<environment-set> <team-boundary> <promotion-policy>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, environments]
model: inherit
effort: high
compatibility: "Designed for Claude Code; environment changes require the corresponding owners"
---
# Ideogram Environment Isolation

## Overview

Prevent development and staging activity from consuming production authority or contaminating production media. Separate keys, application identities, budgets, routes, queues, state, storage, telemetry, and cleanup while recognizing that keys in the same Ideogram team share credits.

## Prerequisites

- Environment inventory, Ideogram team model, billing owner, and promotion owner.
- Secret, queue, webhook, storage, observability, data, and retention maps.
- A synthetic test-data policy and production-access exception process.

## Current Contract

Ideogram supports multiple revocable keys, but keys within one team share credit and billing. Team roles are Owner, Admin, and Member. Environment separation therefore needs application-owned budgets and controls even when separate vendor keys use one shared team.

## Authentication

Create distinct secret references per environment and inject each server-side as `Api-Key` to `https://api.ideogram.ai`. Never copy a production key into developer machines, pull-request jobs, staging configuration, or shared examples.

## Instructions

1. Inventory each environment's key reference, team, role owner, budget, route, queue, webhook URL, storage prefix, telemetry, and data class.
2. Assign distinct keys where supported and document the shared-credit boundary of any common Ideogram team.
3. Enforce application-side environment and tenant budgets, concurrency, and destination allowlists.
4. Use environment-specific webhook hosts and bind every delivery to a known generation, tenant, and environment.
5. Isolate object stores or prefixes, signing keys, retention jobs, and publication targets.
6. Promote immutable code and schema evidence, not prompts, images, URLs, credentials, or in-flight state.
7. Test wrong-key, wrong-webhook, wrong-bucket, and cross-environment access denial plus independent rollback.

## Tool Discipline

Use Read, Glob, and Grep to inspect configuration and infrastructure. Use Write and Edit for approved environment definitions or tests. Do not create keys, copy secrets, add credit, or mutate deployments without the relevant owner.

## Approval Boundaries

Require approval for production access, shared team or balance use, role changes, secret creation or revocation, data copying, external publication, and deployment. Treat emergency production access as time-bounded and auditable.

## Error Handling

- A distinct key does not imply a distinct vendor balance.
- Reject callbacks and objects whose recorded environment differs from the receiver or storage boundary.
- Revoke a key copied across environments and verify all consumers before restoration.

## Output

Return an environment matrix of key references, shared billing, budgets, routes, queues, webhook hosts, stores, data classes, promotion gates, owners, test results, and rollback state. Exclude actual secrets and content.

## Examples

- Keep development offline by default, staging on synthetic paid canaries, and production behind protected deployment approval.
- Report `prod_key_in_nonprod=false; webhook_cross_env=denied; storage_cross_env=denied`.

## Validation

Scan for reused secret values or references, test network and object-store separation, deliver signed wrong-environment fixtures, and rehearse independent rollback. Confirm test assets are absent from production.

## Resources

- [Current first-party evidence map](references/official-docs.md) — use the dated endpoint, webhook, billing, team, and training links as the contract index for this workflow.
- Recheck the endpoint-specific page and current OpenAPI description before relying on an enum, limit, beta feature, or lifecycle claim.
- Record live observations as environment-specific evidence, not as universal vendor guarantees.
