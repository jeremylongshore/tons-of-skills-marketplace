---
name: canva-deploy-integration
description: 'Deploy a Canva Connect backend with exact redirect URIs, runtime-only secrets, protected migrations, and verified rollback. Use when promoting to staging or production. Trigger with: "deploy Canva integration", "configure Canva callback", "release Canva backend".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[target-environment-and-release-id]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - deployment
  - operations
compatibility: 'Requires control of the HTTPS callback domain, approved environment credentials, and a tested rollback artifact.'
---

# Canva Deployment and Callback Gate

## Overview

Promote one immutable application artifact while keeping OAuth configuration and credentials environment-specific. Validate callbacks and a non-mutating Canva read before enabling user traffic.

## Prerequisites

- Reviewed artifact digest and target environment
- Exact registered redirect URI and controlled HTTPS domain
- Secret backend, migration plan, health contract, and rollback version

## Instructions

### Step 1: Compare configuration

Use Read and Grep to diff redirect URI, scopes, preview features, callback/webhook routes, secret references, and data stores against the approved release.

### Step 2: Stage runtime secrets

Inject environment-specific credentials from the approved backend. Never bake secrets or refresh tokens into images, frontend bundles, logs, or deployment output.

### Step 3: Deploy traffic-disabled

Use Write or Edit for reviewed platform configuration, deploy the immutable artifact, run migrations with a rollback plan, and keep external traffic disabled.

### Step 4: Verify callback safety

Confirm exact redirect matching, state validation, PKCE verifier handling, backend-only token exchange, cookie/session controls, and rejection of unexpected hosts.

### Step 5: Run bounded readiness

Use a dedicated test user for a non-mutating identity/metadata read and verify redaction, dependency health, and version. Do not create content in a generic health endpoint.

### Step 6: Promote or roll back

Enable traffic gradually under local SLOs. Restore the prior artifact/config and pause OAuth entry if authorization, data, or readiness evidence diverges.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

The same artifact moves from staging to production while each environment retains separate Canva credentials and redirect URIs. Traffic is enabled only after callback and read-only test evidence passes.

## Error Handling

| Failure | Response |
| --- | --- |
| Redirect URI mismatch | Keep traffic disabled and correct the registered/configured value |
| Secret appears in build output | Contain and rotate it before redeployment |
| Migration is not reversible | Stop promotion until recovery is proven |
| Readiness check mutates Canva | Replace it with a safe identity or metadata read |

## Resources

- [First-party source notes](references/official-docs.md)
- [Creating integrations](https://www.canva.dev/docs/connect/creating-integrations/)
- [Connect security](https://www.canva.dev/docs/connect/guidelines/security/)
