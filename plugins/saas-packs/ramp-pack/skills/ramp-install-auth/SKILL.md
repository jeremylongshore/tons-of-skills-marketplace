---
name: ramp-install-auth
description: >-
  Select and configure the correct Ramp OAuth grant, scopes, environments, and secret lifecycle. Use when bootstrapping an internal server integration or a third-party multi-tenant application. Trigger with "set up Ramp OAuth" or "Ramp client credentials".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, oauth, authentication, installation]
---
# Ramp OAuth Application and Authentication Setup

## Overview

Choose the grant from the trust model. Use Client Credentials for an internal server-to-server integration; use Authorization Code with state and refresh handling for a third-party or multi-tenant application.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Ramp's token endpoint is `/developer/v1/token`, typically using HTTP Basic authentication for the client.
- Client Credentials tokens last 10 days; Authorization Code and refresh-token access tokens last one hour according to the current authorization guide.
- Authorization Code is required for third-party integrations acting for other businesses; its authorization code is short-lived and redirect URI matching is exact.
- Tokens are opaque, environment-bound, and scope-bound; changing configured scopes requires a new token.

## Instructions

1. Identify internal versus third-party architecture, target environments, tenants, redirect origins, required operations, data classes, and accountable application owner.

2. Register separate sandbox and production applications; enable only the selected grant and minimum endpoint scopes.

3. Store client secrets and refresh tokens in an approved secret manager, record rotation/revocation ownership, and prohibit browser or repository exposure.

4. For Authorization Code, generate and verify cryptographically random state and exact HTTPS redirect URIs; for Client Credentials, keep token exchange server-side.

5. Acquire a sandbox token, verify one minimum-scope read plus one denied operation, then document the independently approved production promotion.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

The business owner approves the application; security approves grant, redirects, scopes, and secret lifecycle; each tenant's authorized user grants third-party access.

## Output

An application inventory, architecture/grant decision, scope matrix, redirect and environment map, secret references, token lifecycle, positive/negative proof, and revocation procedure.

## Error Handling

| Condition | Response |
|---|---|
| `invalid_client` | Verify environment-specific client credentials and Basic authentication without exposing values. |
| `invalid_scope` | Align configured and requested scopes, obtain a new token, and repeat negative testing. |
| `Business not authorized` | Have an appropriately privileged business user authorize the app; do not bypass user authority. |

## Examples

### Example 1

Configure an internal accounting worker with Client Credentials and only transaction/accounting scopes in sandbox.

### Example 2

Configure a multi-tenant partner app with Authorization Code, exact redirects, verified state, encrypted refresh tokens, and tenant revocation.

## Validation

- Grant type matches the internal or third-party architecture.
- Sandbox and production use separate apps, hosts, credentials, and evidence.
- Every scope maps to a documented endpoint and owner.
- Secrets are absent from source and logs; rotation, revocation, expiry, and negative tests work.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
