---
name: persona-deploy-integration
description: >-
  Deploy a Persona integration with immutable configuration, event compatibility, canary evidence, and lossless rollback. Use when releasing service changes. Trigger with: "deploy Persona service", "release Persona integration", "rollback Persona change".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[release-sha-and-target]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - persona
  - deployment
  - rollback
  - operations
compatibility: 'Requires an authorized Persona environment, current first-party documentation, a reviewed dated API version, and privacy-safe operational evidence.'
---

# Persona Integration Release and Rollback

## Overview

Deploy code, API version, templates, secrets, event consumers, and domain policy as one reviewed compatibility boundary. Rollback must preserve queued events and understand data already written by the new release.

## Prerequisites

- Immutable artifact and deployment target
- Versioned configuration and secret references
- Database, queue, webhook, canary, and rollback ownership

## Instructions

### Step 1: Build the release manifest

Record artifact digest, API version, template IDs, endpoint IDs, schema versions, flags, secret generations, and approved migrations.

### Step 2: Check compatibility

Prove old and new workers can read queued events and stored evidence across the rollout window. Expand schemas before using new fields.

### Step 3: Stage secrets safely

Bind environment-specific bearer and webhook secrets through the platform secret store. Support bounded overlap for rotations.

### Step 4: Canary a narrow cohort

Observe REST errors, inquiry lifecycle, signature failures, duplicates, queue lag, decisions, latency, rate headroom, and product quotas.

### Step 5: Promote against thresholds

Increase traffic only while evidence remains within the declared error budget. Stop automatically on security, decision, or data-integrity failure.

### Step 6: Rollback without event loss

Restore the previous artifact and configuration, keep compatible consumers running, reconcile in-flight POSTs and inquiries, and replay the durable queue.

## Authentication

Deployment injects secret references, never literal values. A production artifact must be incapable of falling back to a sandbox key or accepting an unsigned webhook.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, resume, approve, decline, redact, rotate, revoke, deploy, or otherwise mutate production Persona resources without explicit operator approval.

## Output

- Immutable release and configuration manifest
- Canary indicators and promotion decisions
- Rollback, queue replay, and reconciliation receipt

Return the environment, resource and event identifiers, API version, template context, source-contract fingerprint, evidence, unresolved risk, rollback state, and final decision without exposing bearer keys, webhook secrets, inquiry session tokens, raw identity documents, or unnecessary PII.

## Examples

A canary reveals the new worker rejects an added event type. Promotion stops, the queue retains deliveries, the old compatible consumer resumes, and the team fixes the tolerant event boundary before retrying.

## Error Handling

| Failure | Response |
| --- | --- |
| Migration is not backward readable | Stop deployment and use an expand-migrate-contract sequence. |
| Signature failures rise | Hold traffic, verify raw-body preservation and secret generation, and do not bypass authentication. |
| Rollback leaves ambiguous POSTs | Reconcile by operation evidence before any replay. |

## Validation

Verify the result against the linked first-party evidence, the pinned API version, redacted contract fixtures, an expected failure path, and the documented rollback or manual-disposition path. A successful request is not proof of a successful identity decision.

## Resources

- [First-party source notes](references/official-docs.md)
- [API introduction](https://docs.withpersona.com/api-introduction)
- [API quickstart](https://docs.withpersona.com/api-quickstart-tutorial)
- [API keys](https://docs.withpersona.com/api-keys)
- [Rate limits](https://docs.withpersona.com/rate-limiting)
- [Webhook best practices](https://docs.withpersona.com/webhooks-best-practices)
- [Request idempotence](https://docs.withpersona.com/idempotence)
