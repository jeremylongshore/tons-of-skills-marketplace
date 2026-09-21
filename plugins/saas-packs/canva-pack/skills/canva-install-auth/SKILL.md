---
name: canva-install-auth
description: 'Implement Canva Connect OAuth 2.0 Authorization Code with SHA-256 PKCE on a backend. Use when creating an integration, adding explicit scopes, handling callback state, or rotating single-use refresh tokens. Trigger with: "set up Canva OAuth", "Canva PKCE", "refresh Canva token".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[redirect-uri-and-required-scopes]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - authentication
  - operations
compatibility: 'Requires a Canva Developer Portal integration, controlled redirect URI, backend secret store, and consent design.'
---

# Canva OAuth Credential Boundary

## Overview

Build authorization as a stateful backend protocol, not a copied token snippet. Keep the PKCE verifier and client secret out of the browser and serialize refresh-token replacement per user.

## Prerequisites

- Developer Portal integration and saved client secret
- Controlled redirect URI and exact explicit scopes
- Backend session, token vault, encryption, and revocation path

## Instructions

### Step 1: Register the integration

Configure name, minimum scopes, at least one controlled redirect URI, and secret storage. Remove localhost and loopback redirect hosts from production configuration.

### Step 2: Create authorization state

Generate high-entropy per-request state and a PKCE verifier that meets Canva's documented character/length rules. Store both server-side with short expiry and one-time use.

### Step 3: Build the authorization URL

Use Canva's authorization endpoint, S256 challenge method, explicit space-separated scopes, client ID, state, and an exactly registered redirect URI.

### Step 4: Validate the callback

Reject missing/mismatched/expired state, repeated codes, unexpected redirect context, and errors before token exchange.

### Step 5: Exchange on the backend

Authenticate the token request using the approved client method, send the verifier and authorization code, validate the response, encrypt access and refresh tokens separately, and discard transient secrets.

### Step 6: Refresh atomically

Single-flight refresh per user because each refresh token is single-use. Commit the new access token, expiry, and replacement refresh token atomically; reauthorize on unrecoverable failure.

### Step 7: Support disconnect

Revoke when required, delete application-held tokens and cached authorization, and record a credential-free receipt.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

A callback consumes a one-time state record and server-held verifier, exchanges the code on the backend, and stores the replacement refresh token in the same transaction that invalidates the prior token.

## Error Handling

| Failure | Response |
| --- | --- |
| State mismatch | Stop the flow and create no token record |
| Verifier missing | Restart authorization; never weaken PKCE |
| Refresh race detected | Serialize by Canva user and retain one authoritative result |
| Scope added later | Update portal configuration and obtain fresh user consent |

## Resources

- [First-party source notes](references/official-docs.md)
- [Authentication](https://www.canva.dev/docs/connect/authentication/)
- [Connect security](https://www.canva.dev/docs/connect/guidelines/security/)
