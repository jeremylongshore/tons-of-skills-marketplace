---
name: ramp-local-dev-loop
description: >-
  Build a safe local Ramp integration loop with schema fixtures, sandbox data, simulated lifecycle events, and explicit production blocking. Use when developing or reproducing API behavior locally. Trigger with "Ramp local development" or "Ramp sandbox test".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, local-development, sandbox, fixtures]
---
# Ramp Sandbox Development Loop

## Overview

Keep the default loop deterministic and offline, then use Ramp sandbox for the smallest behavior that needs vendor execution. Make environment resolution visible and fail closed before any local write can reach production.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Ramp sandbox uses `https://demo.ramp.com` for the UI and `https://demo-api.ramp.com` for Developer API calls.
- Sandbox has no real money movement and supports demo actions for creating transactions and advancing selected bill or reimbursement states.
- Sandbox permissions still affect demo actions and API behavior.
- The official OpenAPI document provides request and response schemas for local fixtures and contract checks.

## Instructions

1. Create a typed environment resolver with explicit `sandbox` default, an allowlist of Ramp hosts, and a hard production-write interlock.

2. Generate minimal sanitized fixtures from the reviewed OpenAPI contract for success, empty page, pagination, error, webhook duplicate, and ambiguous-write cases.

3. Run unit and contract tests offline; assert no credential, card detail, receipt, or personal field enters snapshots or logs.

4. Use a sandbox account and demo actions to create only the lifecycle state under test; record object IDs and reset/cleanup ownership.

5. Compare sandbox observations with fixtures, update only after review, and save the contract checksum and exact test artifact.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

Developers may use approved sandbox data and credentials. Any production read, production credential, real business data, or write requires separate owner approval.

## Output

A fail-closed environment resolver, sanitized fixture set, deterministic test results, sandbox scenario receipt, contract checksum, and cleanup record.

## Error Handling

| Condition | Response |
|---|---|
| Local code resolves `api.ramp.com` | Abort before token acquisition or network access and correct configuration precedence. |
| Sandbox has no matching state | Create it through documented demo actions or API setup; do not copy production data. |
| A snapshot contains sensitive fields | Delete the fixture from working copies, rotate exposed credentials if any, and replace it with synthetic schema-valid data. |

## Examples

### Example 1

Simulate a sandbox transaction, receive its webhook fixture, process it twice, and prove one downstream effect.

### Example 2

Reproduce a 422 locally from the schema, then confirm the corrected request in sandbox without widening scopes.

## Validation

- Offline tests are the default and credential-free.
- All outbound hosts pass an explicit sandbox allowlist during local development.
- Fixtures are schema-valid, synthetic, and scrubbed.
- Sandbox object lifecycle and cleanup are reproducible.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
