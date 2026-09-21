---
name: ramp-core-workflow-a
description: >-
  Build and verify a fund-backed Ramp virtual-card workflow with least-privilege scopes, idempotency, controlled card-detail delivery, and lifecycle evidence. Use when issuing virtual cards or embedding card details. Trigger with "issue Ramp virtual card" or "Ramp embedded card".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, cards, funds, spend-controls]
---
# Ramp Fund-Backed Virtual Card Workflow

## Overview

Create the spend authority first, then issue or expose the card through the supported delivery surface. Prefer Ramp's embedded iframe when a person needs to see card details; use the Vault API only for an approved server-side payment flow.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Current virtual cards are backed by Funds and governed by spend controls; legacy Cards management endpoints are being deprecated.
- Embedded Cards sends card details directly from a Ramp-hosted iframe to the user's browser, keeping the application server out of the card-data plane.
- The Vault API returns PAN, CVV, and expiration to a backend and requires Ramp production approval plus materially stronger PCI controls.
- New embedded integrations use the business-specific iframe URL and an exactly matching, verified HTTPS parent origin.

## Authentication

Use a server-side Ramp OAuth bearer token from the selected environment with only the required Funds, Virtual Cards, or Embedded Cards scopes. Never send the bearer token to browser code; the backend mints the short-lived embed token. Vault access also requires its documented scopes and Ramp production approval.

## Instructions

1. Record the cardholder or service purpose, business entity, owner, amount and interval, eligible spend, expiration, approval path, and termination trigger.

2. Choose embedded iframe or Vault delivery and document why the lower-exposure option is insufficient if selecting Vault.

3. In sandbox, create the required Fund or spend-control object with a unique idempotency key, then capture the returned card identifier without card details.

4. For embedded delivery, verify the exact parent origin and mint short-lived embed tokens on demand from the backend; never expose the Ramp access token to the browser.

5. Exercise suspension or fund termination, reconcile final state through a read, and preserve the approval, object IDs, idempotency keys, and rollback result.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

The budget owner approves spend authority; the application and security owners approve delivery architecture. Vault production access requires Ramp approval and the organization's PCI review.

## Output

A purpose-and-control record, scope matrix, sandbox creation receipt, safe delivery design, lifecycle verification, and named owner for suspension, termination, and incident response.

## Error Handling

| Condition | Response |
|---|---|
| Origin verification fails | Confirm exact HTTPS origin, public verification file bytes, timeout, and absence of redirects or wildcard hosts. |
| A create response is ambiguous | Query by the durable business key or reconcile the deferred task before reusing the idempotency key. |
| A backend receives card details unexpectedly | Contain the data, stop logging, involve security, and redesign around the embedded iframe unless Vault is explicitly approved. |

## Examples

### Example 1

Issue a monthly software fund and virtual card, render it through a verified staging iframe, then terminate the sandbox fund.

### Example 2

Design an approved backend travel-booking flow using Vault while keeping card data out of general logs, queues, and analytics.

## Validation

- The card is attached to an approved Fund and the controls match the business purpose.
- Scopes, environment, entity, user, and approval are minimum and recorded.
- Card details travel only through the selected approved delivery surface.
- Duplicate submission, suspension, termination, and reconciliation behavior are proven.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
