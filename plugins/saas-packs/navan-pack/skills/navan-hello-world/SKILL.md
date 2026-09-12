---
name: navan-hello-world
description: >-
  Prove one contracted Navan integration can authenticate and return a bounded read-only response without inventing a universal API. Use when completing access intake. Trigger with "test Navan access", "first Navan read", or "Navan connectivity proof".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<tenant> <surface> <approved-read>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, connectivity]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Read-Only Connectivity Proof

## Overview

Prove one contracted Navan integration can authenticate and return a bounded read-only response without inventing a universal API. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

The public site confirms downstream Booking API access and an Expense API for custom ERP integrations, but it does not publish a universal route or response schema. The selected tenant's current contract is the only execution authority.

## Authentication

Resolve the approved non-production credential at runtime and bind it only to the documented host. Redact headers, query values, traveler identities, booking details, and expense data from evidence.

## Instructions

1. Select the smallest documented read operation for the enabled surface.
2. Copy its method, host, path, parameters, and response schema into a dated local contract fixture.
3. Set a short timeout, response-size bound, and zero automatic retries.
4. Run only after network and data-access approval is explicit.
5. Validate status, content type, required fields, pagination envelope, and redaction.
6. Store a content-free receipt and revoke temporary credentials when required.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Network access, a real credential, and any response containing traveler or expense information require explicit approval; no write or booking action belongs in this proof.

## Error Handling

- Treat redirects or HTML as contract mismatch, not success.
- Do not print response bodies on authentication or schema failure.
- Stop on an undocumented host, method, pagination rule, or write effect.

## Output

Return the contract revision, operation identifier, bounded result metadata, redaction result, elapsed time, and rollback or revocation status. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Validate a one-record Booking API read defined in the tenant docs.
- Confirm an Expense API metadata response without downloading receipts.

## Validation

Re-run with a missing secret, wrong tenant, timeout, oversized response, schema drift, and denied network approval. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
