---
name: ramp-hello-world
description: >-
  Verify Ramp OAuth, environment, pagination, and monetary parsing with a bounded read-only transaction call. Use when checking credentials or preparing to enable a new integration. Trigger with "test Ramp connection" or "first Ramp API call".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, quickstart, transactions, verification]
---
# Ramp Read-Only Connectivity Proof

## Overview

Prove the smallest useful path: obtain a token without exposing it, call the current Developer API transaction surface with minimum scope, inspect the response envelope, and record a sanitized environment receipt.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- The current Developer API path is `/developer/v1`; the production host is `api.ramp.com` and the sandbox host is `demo-api.ramp.com`.
- The quickstart obtains a token from `/developer/v1/token` and reads transactions with `transactions:read`.
- List responses use a `data` collection and page metadata; callers must follow the documented cursor rather than assume one page is complete.
- Most Ramp monetary values are integers in the smallest unit of the accompanying currency, subject to the endpoint schema.

## Authentication

Acquire a server-side OAuth bearer token from `/developer/v1/token` using the approved grant and minimum `transactions:read` scope. Keep the client secret and token out of source, browser code, logs, and evidence.

## Instructions

1. Resolve the target environment, app owner, grant type, `transactions:read` scope, and approved secret-store references.

2. Acquire the token using the current authorization flow; retain only expiry, scope names, environment, and a one-way token-instance identifier.

3. Request the smallest documented transaction page from `/developer/v1/transactions`, with no write scope and no production query wider than approved.

4. Validate status, content type, `data`, page metadata, transaction IDs, amount representation, currency, and `x-trace-id`; redact people and merchant details.

5. Test one denial using an ungranted operation or sandbox-only client, then save the sanitized pass/fail receipt and next cursor behavior.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

The application owner approves client use; the data owner approves any production transaction read. No write or scope expansion is part of this proof.

## Output

An environment and grant record, sanitized token metadata, bounded transaction response shape, cursor observation, trace ID, negative test, and explicit go/no-go for further work.

## Error Handling

| Condition | Response |
|---|---|
| The endpoint returns 401 | Verify the token host, grant, secret provenance, expiry, and Authorization header without printing the token. |
| The endpoint returns 403 | Compare configured and token-bound `transactions:read` plus the principal's business access. |
| Amounts look 100 times too large | Read the endpoint's monetary schema and preserve integer minor units until presentation. |

## Examples

### Example 1

Prove sandbox connectivity with a two-record transaction page and a denied card-write attempt.

### Example 2

Run an approved production read for one page, redact the payload, and preserve only shape, count, cursor, trace ID, and environment.

## Validation

- The request uses `/developer/v1` on the intended host.
- The token and client secret never appear in source, terminal history, logs, or evidence.
- The response parser handles an empty `data` list and a continuation cursor.
- The read and negative test match the approved scope boundary.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
