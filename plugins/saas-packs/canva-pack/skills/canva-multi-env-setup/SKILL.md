---
name: canva-multi-env-setup
description: 'Configure isolated development, staging, and production Canva integrations. Use when separating redirect URIs, credentials, users, token stores, scopes, data, and audit evidence across environments. Trigger with: "Canva environments", "Canva staging setup", "separate Canva credentials".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[environment-set-and-secret-backend]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - environments
  - operations
compatibility: 'Requires controlled domains and an approved secret backend for every named environment.'
---

# Canva Environment Isolation

## Overview

Give each environment an independent Canva integration and trust boundary. Prevent a staging build, callback, credential, user, or token record from resolving to production.

## Prerequisites

- Named environments, owners, domains, and deployment identities
- Separate Developer Portal integrations and redirect URIs
- Secret backend, token namespace, test-user, data, and audit policy per environment

## Instructions

### Step 1: Build the matrix

Use Read and Grep to map environment to integration ID, exact redirect hosts, scopes, preview features, secret references, token/data namespace, and owners.

### Step 2: Separate integrations

Create or verify distinct Canva integrations where isolation is required. Never distinguish environments only with a runtime variable while sharing credentials.

### Step 3: Constrain configuration

Use Write or Edit to validate environment identity, controlled host allowlists, exact callback routes, expected integration ID, and forbidden cross-environment values at startup.

### Step 4: Isolate secrets and tokens

Use separate secret paths, encryption keys where policy requires, access policies, token tables or namespaces, backup rules, and rotation owners.

### Step 5: Isolate users and data

Use synthetic development/staging users and assets. Prevent non-production workers, webhooks, or support tooling from reading production records.

### Step 6: Test negative boundaries

Prove staging cannot use production client secrets, callbacks, tokens, queues, databases, or webhook routes; fail closed on mismatch.

### Step 7: Record promotion rules

Document which artifact is shared, which configuration must differ, rollback, environment cleanup, and evidence needed before production.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

The same reviewed artifact runs in staging and production, but startup validation requires different integration IDs, callback hosts, vault paths, token namespaces, and test policies.

## Error Handling

| Failure | Response |
| --- | --- |
| Two environments share a secret | Stop deployment and separate/rotate credentials |
| Callback host is unexpected | Reject the request before token exchange |
| Production token appears in staging | Contain, revoke, and audit the cross-boundary path |
| Environment matrix is stale | Block promotion until owners reconfirm it |

## Resources

- [First-party source notes](references/official-docs.md)
- [Creating integrations](https://www.canva.dev/docs/connect/creating-integrations/)
- [Connect security](https://www.canva.dev/docs/connect/guidelines/security/)
