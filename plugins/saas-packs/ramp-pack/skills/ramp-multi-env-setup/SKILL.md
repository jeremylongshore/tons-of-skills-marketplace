---
name: ramp-multi-env-setup
description: >-
  Configure isolated Ramp sandbox, staging, and production environments with separate applications, credentials, hosts, data, webhooks, and evidence. Use when preventing cross-environment access or promoting an integration. Trigger with "Ramp environments" or "separate Ramp sandbox and prod".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, environments, configuration, safety]
---
# Ramp Sandbox and Production Isolation

## Overview

Make environment selection a typed security boundary. Keep credentials and data from crossing it, verify resolved hosts before token exchange, and require an explicit interlock before production writes.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Ramp sandbox uses `demo.ramp.com` and `demo-api.ramp.com`; production uses `app.ramp.com` and `api.ramp.com`.
- Tokens are valid only in the environment where issued, and sandbox and production applications have independent credentials and settings.
- Production Embedded Cards origins must be exact verified HTTPS origins; localhost is not accepted for production integrations.
- Sandbox cannot move real money, but its successful behavior does not prove production authorization or data equivalence.

## Instructions

1. Define a closed environment enum with host, application ID, secret references, redirect URIs, parent origins, webhook endpoints, entity allowlists, and write policy.

2. Create separate Ramp applications and secret-manager namespaces; prohibit a configuration from carrying credentials or webhook secrets across environments.

3. Validate host allowlists, TLS, redirect/origin exactness, and token environment before each startup; print only non-secret environment identity.

4. Run synthetic and sandbox tests, then promote the same artifact and reviewed configuration schema without copying sandbox data or credentials.

5. Require a time-bound production-write enablement with owner, entity, operation, rollback, and automatic fail-closed behavior.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

Security owns isolation and secrets; application owners approve hosts and redirects; business/finance owners approve production entity access and writes.

## Output

An environment matrix, validated configuration schema, application and secret inventory, host/origin proof, isolation tests, promotion record, and write-interlock evidence.

## Error Handling

| Condition | Response |
|---|---|
| A token fails only after promotion | Verify the production application, scopes, grant, secret reference, and host; never fall back to sandbox credentials. |
| A production origin contains localhost or a wildcard | Block release and configure the exact controlled HTTPS origin. |
| Environment is missing or unknown | Fail closed before reading credentials or constructing a request. |

## Examples

### Example 1

Configure local and CI to permit only `demo-api.ramp.com`, while production accepts only `api.ramp.com` with a separate secret namespace.

### Example 2

Verify staging and production webhook endpoints use different subscriptions, secrets, queues, and replay ledgers.

## Validation

- Each environment has unique applications, credentials, webhooks, data, and evidence.
- Unknown or mixed configuration fails before network access.
- Production writes require an explicit bounded enablement.
- Positive and negative tests prove host, token, redirect, origin, entity, and secret isolation.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
