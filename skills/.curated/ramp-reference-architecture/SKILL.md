---
name: ramp-reference-architecture
description: >-
  Design a production Ramp integration with isolated OAuth clients, typed API adapters, durable webhook ingestion, reconciliation workers, and audited financial writes. Use when reviewing architecture or building a new platform. Trigger with "Ramp architecture" or "design Ramp integration".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, architecture, integration, governance]
---
# Ramp Integration Reference Architecture

## Overview

Separate trust and failure domains: credential broker, typed adapter, event ingress, durable work ledger, financial connectors, reconciliation, and evidence. Keep write authority narrower than read and observability paths.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Ramp supports direct Developer API, webhooks, MCP, and CLI surfaces for different automation jobs; long-lived deterministic integrations belong on the Developer API.
- Webhook events are notifications and may be duplicated or out of order; fetch current resource state before acting when needed.
- OAuth grant, scope, principal, entity, and object policy jointly determine authority.
- Accounting and card workflows have distinct approval, idempotency, sensitive-data, and reconciliation requirements.

## Instructions

1. Define business capabilities, actors, tenants/entities, latency, volumes, data classes, financial effects, recovery objectives, and prohibited actions.

2. Partition separate OAuth applications and services for read-only ingestion, event receipt, accounting writes, and card/spend authority where trust differs.

3. Place an allowlisted typed adapter behind secret-managed token acquisition; centralize rate budget, pagination, error parsing, trace IDs, and schema-version evidence.

4. Ingest verified webhooks into a durable deduplicating queue, process asynchronously, and reconcile current API state plus downstream effects on a schedule.

5. Design deployment, observability, incident isolation, data retention, negative-access tests, and rollback; threat-model every path that can spend, sync, or expose card data.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

Architecture, security, privacy, business, and finance owners approve boundaries. Ramp approval is required for vendor-restricted surfaces such as production Vault access.

## Output

A context and data-flow design, trust boundaries, application/scope matrix, component ownership, event/reconciliation model, threat analysis, SLOs, rollout, and rollback.

## Error Handling

| Condition | Response |
|---|---|
| One service holds every scope | Split authority by capability and lifecycle, then retest cross-boundary denial. |
| Webhooks directly perform financial writes | Insert a durable deduplicating ledger and reconcile current state before side effects. |
| Observability needs raw payloads | Design field-safe structured signals and restricted evidence access instead. |

## Examples

### Example 1

Design a read-only warehouse exporter with webhook triggers and periodic reconciliation, isolated from accounting-write credentials.

### Example 2

Design an ERP connector whose source ledger, downstream receipt, and Ramp sync receipt form one auditable state machine.

## Validation

- Every component has a single trust purpose, owner, and failure boundary.
- Secrets, card data, identity data, and financial writes follow minimized paths.
- Duplicates, out-of-order events, timeouts, partial failure, and replay are modeled.
- Authority and reconciliation have positive and negative verification.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
