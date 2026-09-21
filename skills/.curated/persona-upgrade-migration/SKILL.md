---
name: persona-upgrade-migration
description: >-
  Migrate between dated Persona API versions using inventory, contract fixtures, dual-read evidence, and rollback. Use when changing Persona-Version. Trigger with: "upgrade Persona API", "migrate Persona version", "update Persona-Version".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[from-version-to-version]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - persona
  - migration
  - api-version
  - compatibility
compatibility: 'Requires an authorized Persona environment, current first-party documentation, a reviewed dated API version, and privacy-safe operational evidence.'
---

# Dated Persona API Version Migration

## Overview

Treat `Persona-Version` as a contract migration. Because the request header overrides the key’s configured version and compatible releases can add or reorder data, migrate parsers, webhook handling, and operational evidence together.

## Prerequisites

- Source and target dated API versions
- Endpoint, resource, event, and consumer inventory
- Representative redacted fixtures plus a reversible rollout mechanism

## Instructions

### Step 1: Freeze the baseline

Record API-key configured versions, explicit headers, endpoints, templates, response hashes, events, dashboards, and consumer assumptions.

### Step 2: Read the provider delta

Map documented breaking and compatible changes to each request, JSON:API mapper, event handler, policy rule, test, and data export.

### Step 3: Harden for additions

Make parsers tolerate new resources, fields, types, event types, and array ordering before switching the header.

### Step 4: Build dual-version fixtures

Capture or synthesize equivalent source and target responses for success, error, pagination, inquiry sessions, verifications, and webhooks.

### Step 5: Canary the explicit header

Send the target `Persona-Version` for a bounded cohort and compare transport, resource, event, decision, latency, and quota metrics.

### Step 6: Promote with rollback

Change the explicit header and key configuration deliberately, retain source-version compatibility during the observation window, and document the rollback trigger.

## Authentication

Test source and target versions with appropriately scoped keys. The explicit request header is authoritative for that request, so accidental fallback to a key default is a gate failure.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, resume, approve, decline, redact, rotate, revoke, deploy, or otherwise mutate production Persona resources without explicit operator approval.

## Output

- Version delta and affected-consumer inventory
- Dual-version fixture and canary comparison
- Promotion, observation, rollback, and retirement receipt

Return the environment, resource and event identifiers, API version, template context, source-contract fingerprint, evidence, unresolved risk, rollback state, and final decision without exposing bearer keys, webhook secrets, inquiry session tokens, raw identity documents, or unnecessary PII.

## Examples

A parser that assumes a closed verification-type enum is changed to preserve unknown values before the canary. The target version then runs for five percent of traffic while decisions and webhook reconciliation are compared.

## Error Handling

| Failure | Response |
| --- | --- |
| Key and header versions disagree | Record both and use the reviewed explicit header; remove accidental ambiguity before rollout. |
| Target response breaks a consumer | Roll back the cohort, add a versioned mapper or tolerant parser, and rerun fixtures. |
| Rollback cannot read new events | Do not promote until forward-compatible event handling exists. |

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
