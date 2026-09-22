---
name: ramp-security-basics
description: >-
  Establish least-privilege OAuth, secret, webhook, data, card, and financial-write controls for a Ramp integration. Use when threat modeling, reviewing a launch, or remediating controls. Trigger with "secure Ramp integration" or "Ramp security review".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, security, secrets, threat-modeling]
---
# Ramp Integration Security Baseline

## Overview

Protect credentials and financial authority as separate assets. Minimize scopes and data paths, verify webhook authenticity from raw bytes, and require idempotent, approved, reconciled writes.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Ramp access tokens are opaque bearer credentials bound to environment and scope; they must not be logged or exposed to browser code.
- Webhook subscriptions return a secret and deliveries include `X-Ramp-Signature`, an HMAC-SHA256 signature over the exact raw request body.
- Embedded Cards can keep PAN/CVV outside application servers; Vault brings card data into the backend and requires production approval.
- Authorization Code flows require strong state verification and exact redirect URIs; Client Credentials is for internal server-side integrations.

## Instructions

1. Threat-model clients, redirects, token exchange, secret stores, API adapters, webhook ingress, queues, logs, card delivery, accounting writes, admin access, and support paths.

2. Split applications by trust boundary, request minimum scopes, isolate environments and tenants/entities, and assign rotation plus emergency revocation owners.

3. Verify webhook signatures over raw bytes before parsing, validate expected event type and business, deduplicate by event ID, and process asynchronously.

4. Prefer embedded card delivery; isolate any approved Vault service and prohibit PAN/CVV from logs, queues, analytics, support tools, and general databases.

5. Test stolen-token containment, replay, cross-tenant/entity denial, redirect/state failure, secret rotation, webhook-secret rotation, and financial-write reconciliation.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

Security owns client and secret controls; privacy/data owners approve fields; finance/business owners approve write authority; Ramp approves restricted production card surfaces.

## Output

A threat model, client/scope matrix, secret inventory, webhook verification design, card-data boundary, write-control ledger, test receipts, and incident contacts.

## Error Handling

| Condition | Response |
|---|---|
| Signature verification fails after JSON parsing | Capture and verify the exact raw body before any parser or middleware mutation. |
| A secret appears in source or logs | Revoke and rotate, restrict evidence, remove downstream copies, and add prevention tests. |
| A read client can write | Revoke or replace its token, narrow scopes/application design, and add a negative test. |

## Examples

### Example 1

Secure a webhook receiver with raw-body HMAC verification, stable event-ID dedupe, tenant checks, and a durable queue.

### Example 2

Move card display to Ramp's hosted iframe and prove the backend no longer receives card details.

## Validation

- Every credential and write capability has minimum scope, owner, rotation, revocation, and negative tests.
- Webhook authenticity and replay controls operate before business processing.
- Secrets and card details are absent from routine storage and telemetry.
- Cross-environment, cross-tenant, cross-entity, and over-scope access fail.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
