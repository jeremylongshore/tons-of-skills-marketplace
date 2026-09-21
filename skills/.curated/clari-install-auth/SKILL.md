---
name: clari-install-auth
description: >-
  Configure a least-privilege Clari identity and validate Revenue API or Copilot credentials without exposing secrets. Use when starting an integration or rotating access. Trigger with: "set up Clari auth", "configure a Clari token", "test Copilot credentials".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[surface-revenue-or-copilot-and-environment]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - clari
  - authentication
  - tokens
  - integration-user
compatibility: 'Requires an entitled Clari tenant, an approved integration owner, and access to the relevant Revenue API or conversation-intelligence workspace settings.'
---

# Clari Integration Identity and Token Setup

## Overview

Establish a dedicated integration identity before building any data flow. Treat Revenue API tokens, ingestion partner keys, and Copilot key/password pairs as separate credentials with separate rotation and revocation paths.

## Prerequisites

- Named business owner and technical owner for the integration
- Target surface: Revenue API, v2 ingestion, or Copilot API
- Approved secret manager and a non-production validation boundary

## Instructions

### Step 1: Choose the surface

Record the exact base URL and authentication contract: Revenue API uses the `apikey` header, v2 ingestion additionally requires `partnerkey`, and Copilot uses both `X-Api-Key` and `X-Api-Password`.

### Step 2: Create a dedicated identity

Use a service or integration user whose hierarchy and forecast access match the intended export scope. Do not reuse a personal administrator credential.

### Step 3: Issue and escrow credentials

Generate the credential in the Clari settings exposed for the entitled product, capture it once into the approved secret manager, and record owner and rotation metadata without copying the value into tickets or logs.

### Step 4: Validate the smallest read

For Revenue API, call the administrative limits read or another entitled read-only endpoint. For Copilot, list a narrowly scoped resource such as users; do not create or update CRM records during authentication testing.

### Step 5: Prove effective access

Confirm the identity can see only the expected organization, forecast hierarchy, workspace, and object set. Treat an empty result separately from successful authorization.

### Step 6: Document rotation and revocation

Define overlap, rollback, dependent-job restart, and emergency revocation procedures before production use.

## Authentication

Send credentials only in the provider-documented headers over HTTPS. Redact all token and password values, never persist them in shell history or fixtures, and remember that revoking a Revenue API token or deactivating its owning user can break active integrations.

## Tool Discipline

Use Read and Grep to inspect configuration, provider contracts, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not issue, rotate, revoke, create, update, cancel, delete, export, ingest, or publish provider data without explicit operator approval.

## Output

- Credential inventory containing references, owners, scopes, and rotation dates
- Redacted read-only validation receipt with endpoint, timestamp, and status
- Revocation and dependent-job recovery plan

Return the exact surface, environment, resource or job identifiers, contract fingerprint, evidence, unresolved risks, and final decision without exposing credentials or sensitive customer data.

## Examples

A forecast warehouse integration receives a dedicated user and token limited by the user’s Clari hierarchy. The operator validates `/admin/limits`, records only the HTTP status and organization context, and schedules a rotation drill before enabling exports.

## Error Handling

| Failure | Response |
| --- | --- |
| 401 or authentication failure | Verify the correct header contract and secret reference; rotate rather than printing the credential. |
| 403 or missing data | Check product entitlement, hierarchy opt-in, forecast access, partner enablement, and workspace scope. |
| Credential owner is deactivated | Issue a replacement under an approved integration identity and restart dependents only after read-only validation. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Clari Revenue API reference](https://developer.clari.com/default/documentation/external_spec)
- [Clari Copilot API reference](https://api-doc.copilot.clari.com/)
