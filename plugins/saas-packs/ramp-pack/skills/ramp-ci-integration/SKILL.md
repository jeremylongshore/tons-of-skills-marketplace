---
name: ramp-ci-integration
description: >-
  Build deterministic CI gates for a Ramp integration using the official OpenAPI contract, local fixtures, and explicitly approved sandbox probes. Use when adding pull-request checks, schema drift detection, or release evidence. Trigger with "Ramp CI" or "test Ramp integration".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, ci, testing, sandbox]
---
# Ramp Sandbox Contract Tests and CI Gates

## Overview

Separate fast deterministic contract checks from credentialed sandbox smoke tests. CI should reject schema drift and unsafe production targeting without making financial writes or depending on mutable live data.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Ramp publishes a canonical OpenAPI document for the Developer API and machine-readable guide exports for current behavior.
- The sandbox is isolated from production and cannot move real money; its current API host is `https://demo-api.ramp.com`.
- Credentialed checks still require the minimum OAuth scopes, and production credentials do not belong in pull-request jobs.
- Unknown fields may be ignored by some endpoints and rejected by others, so request fixtures must be validated against the exact endpoint schema.

## Instructions

1. Pin a reviewed copy or checksum of the official OpenAPI document and generate schema fixtures from only the endpoints the integration uses.

2. Run unit tests with sanitized success, validation, authorization, rate-limit, timeout, and pagination fixtures; assert secret redaction and idempotency behavior.

3. Add a drift job that compares the pinned contract with the current official document and produces a human-reviewed change report instead of silently regenerating clients.

4. Gate credentialed sandbox smoke tests behind trusted branches and protected secrets; prove the resolved host is `demo-api.ramp.com` before any request.

5. Publish the exact commit, contract checksum, deterministic results, optional sandbox result, and production-block assertion as release evidence.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

A repository owner approves CI policy; a security owner approves protected sandbox credentials. Production probes, real financial writes, and automated client regeneration require separate explicit approval.

## Output

A CI gate map, pinned contract receipt, deterministic test results, sanitized sandbox smoke receipt, drift report, and documented release/rollback decision.

## Error Handling

| Condition | Response |
|---|---|
| A fork cannot access secrets | Keep deterministic tests mandatory; mark the trusted sandbox probe as unavailable rather than weakening the gate. |
| The OpenAPI diff is large | Classify breaking, additive, and documentation-only changes; regenerate only after endpoint-owner review. |
| A test resolves a production host | Fail closed before network access and rotate any credential exposed to the job. |

## Examples

### Example 1

Add a pull-request gate that validates transaction fixtures and proves a sandbox token cannot access an ungranted resource.

### Example 2

Detect a changed accounting schema, attach the OpenAPI diff, and block release until mappings and fixtures are reviewed.

## Validation

- Deterministic checks run without Ramp credentials or network access.
- Every live smoke request resolves to sandbox and uses a read-only or explicitly approved simulated workflow.
- The official contract checksum, exact commit, and test result are preserved.
- Logs contain no access token, client secret, card data, receipt image, or personal data.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
