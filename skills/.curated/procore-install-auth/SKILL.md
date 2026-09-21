---
name: procore-install-auth
description: >-
  Choose and implement the correct Procore OAuth 2.0 boundary for a user-facing app or headless data connector. Use when registering credentials, selecting Authorization Code versus DMSA Client Credentials, caching tokens, or planning revocation. Trigger with: "set up Procore auth", "choose Procore OAuth flow", "configure a Procore DMSA".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[app-type-and-required-tools]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - authentication
  - oauth
compatibility: 'Requires a Procore Developer account, an approved secret store, and network access to the selected Procore environment.'
---

# Procore OAuth and DMSA Boundary

## Overview

Select authentication from the actor model, not implementation convenience. User-facing applications normally use Authorization Code, while unattended connectors use Client Credentials through a Developer Managed Service Account whose manifest permissions bound access.

## Prerequisites

- Named application owner and classified user-facing or headless workload
- Exact company-level and project-level tools the workload must access
- Approved callback, secret store, token cache, rotation owner, and revocation path

## Instructions

### Step 1: Choose the grant

Use Authorization Code when the integration acts as a Procore user. Use Client Credentials only for a DMSA or explicitly governed service account that operates without user context.

### Step 2: Define least privilege

List required tool operations before building the app manifest. For a DMSA, encode only those company and project permissions, and require the administrator to select permitted projects during installation.

### Step 3: Separate credentials

Keep production and Developer Sandbox credentials, tokens, login hosts, and API hosts isolated. Never accept a token minted for one environment in another environment's configuration.

### Step 4: Implement token lifecycle

Exchange credentials only from a confidential backend, cache the returned Bearer token until its reported expiry, serialize refresh-token replacement for Authorization Code clients, and persist a newly rotated refresh token atomically.

### Step 5: Prove the boundary

Run one permitted read and one expected-denial test. Include `Procore-Company-Id` where the endpoint or Multiple Procore Regions contract requires company routing.

### Step 6: Revoke and rotate

Document how an operator revokes authorization, replaces credentials, observes the new credential, and removes the old one without logging secrets.

## Authentication

Procore REST requests use OAuth 2.0 Bearer tokens. Authorization Code represents a logged-in user's permissions; Client Credentials represents a DMSA's configured permissions and permitted projects. Keep client secrets and tokens server-side, and never place them in evidence.

## Tool Discipline

Use Read and Grep to inspect application manifests, endpoint requirements, and existing configuration. Use Write or Edit only for the approved configuration, code, test, or redacted receipt; do not change Procore permissions or installations without administrator approval.

## Output

- Grant-selection decision and least-privilege permission inventory
- Environment-specific credential and token-lifecycle configuration
- Positive, negative, rotation, and revocation evidence with secrets removed

Return a concise receipt containing the app type, grant, environment, permitted tools, test outcomes, and rollback owner.

## Examples

A nightly project synchronizer uses a DMSA Client Credentials grant with read access only to the required tools and selected projects. A browser application that edits on behalf of a superintendent instead uses Authorization Code and inherits that user's access.

## Error Handling

| Failure | Response |
| --- | --- |
| Token request rejects the client | Stop retries; verify environment, grant, credential source, and app installation. |
| Refresh token is rejected | Re-authorize the user; do not reuse a refresh token after a successful exchange. |
| Permitted call returns 403 or hidden 404 | Check DMSA tool permission, project membership, installation, and company routing. |
| Credential may be exposed | Revoke or rotate immediately, invalidate caches, and scrub derived artifacts. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Choose an authentication method](https://developers.procore.com/documentation/oauth-choose-grant-type)
- [Client Credentials grant](https://developers.procore.com/documentation/oauth-client-credentials)
- [Developer Managed Service Accounts](https://developers.procore.com/documentation/developer-managed-service-accounts)
