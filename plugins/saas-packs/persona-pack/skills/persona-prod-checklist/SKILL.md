---
name: persona-prod-checklist
description: >-
  Validate a Persona integration for production with evidence across identity flow, privacy, security, reliability, and rollback. Use when preparing a go-live. Trigger with: "launch Persona", "Persona production checklist", "approve Persona go-live".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[release-sha-and-environment]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - persona
  - production
  - readiness
  - release
compatibility: 'Requires an authorized Persona environment, current first-party documentation, a reviewed dated API version, and privacy-safe operational evidence.'
---

# Persona Production Readiness Gate

## Overview

A production key and passing happy path are not enough. The gate must prove environment isolation, template governance, API-version compatibility, authentic replay-safe webhooks, quota behavior, privacy controls, manual review, rollback, and accountable approval.

## Prerequisites

- Immutable release SHA and production architecture
- Named security, privacy, compliance, product, and operations approvers
- Sandbox evidence matching the intended production configuration

## Instructions

### Step 1: Freeze release inputs

Record code SHA, API version, templates and versions, endpoint IDs, domains, environment, feature flags, and migration plan.

### Step 2: Verify access and privacy

Prove least-privilege keys, secret rotation, PII minimization, retention, access logging, customer rights, redaction governance, and incident response.

### Step 3: Exercise identity paths

Run synthetic pass, fail, retry, abandon, resume, unknown-verification, duplicate-customer, and manual-review scenarios.

### Step 4: Prove event reliability

Verify raw-body HMAC, rotation candidates, duplicate delivery, out-of-order delivery, queue recovery, dead-letter replay, and GET reconciliation.

### Step 5: Test limits and failures

Exercise 429 handling, product-quota exhaustion, provider timeout, ambiguous POST, dependency outage, and degraded manual path.

### Step 6: Approve release and rollback

Require named approvals, deploy a narrow cohort, watch defined indicators, and demonstrate rollback without losing authoritative events or decisions.

## Authentication

Production readiness requires production credentials to remain in the production secret boundary. Tests should prove bindings and permissions without exporting their values.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, resume, approve, decline, redact, rotate, revoke, deploy, or otherwise mutate production Persona resources without explicit operator approval.

## Output

- Pass/fail gate matrix with linked evidence
- Named exceptions, owners, expiry dates, and residual risk
- Release, observation, rollback, and final approval receipt

Return the environment, resource and event identifiers, API version, template context, source-contract fingerprint, evidence, unresolved risk, rollback state, and final decision without exposing bearer keys, webhook secrets, inquiry session tokens, raw identity documents, or unnecessary PII.

## Examples

The release stays blocked because the happy path passes but duplicate webhook delivery creates two domain transitions. The team fixes event-ID uniqueness, replays the evidence set, and obtains a new approval for the same release SHA.

## Error Handling

| Failure | Response |
| --- | --- |
| Evidence belongs to another SHA | Invalidate it and rerun the affected gates against the candidate release. |
| Production template drift | Stop rollout until the template and expected verification policy are reconciled. |
| Rollback loses queued events | Keep the release blocked and redesign the compatibility or replay boundary. |

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
