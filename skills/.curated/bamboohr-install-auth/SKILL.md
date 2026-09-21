---
name: bamboohr-install-auth
description: >-
  Choose and configure BambooHR OAuth 2.0 or API-key authentication without
  leaking HR credentials. Use when registering a partner integration, wiring
  token refresh, or repairing tenant authentication. Trigger with "BambooHR
  auth", "BambooHR OAuth", "BambooHR API key", or "BambooHR token refresh".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<oauth|api-key> <tenant-subdomain>"
version: 1.5.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, hr, bamboohr, authentication, oauth]
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# BambooHR Authentication Setup

## Overview

Configure the narrowest BambooHR identity that fits the integration. OAuth 2.0
is BambooHR's recommended path for partner integrations. An API key is suitable
for an internal tool or prototype when its owning user's permissions and key
lifecycle are acceptable.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The tenant, identity, and data scope only when approved live work is in scope.
- The current evidence register plus customer-specific permissions and agreements.

## Current Contract

- Tenant API host: `https://{company-subdomain}.bamboohr.com`.
- Authorization endpoint: `https://{company-subdomain}.bamboohr.com/authorize.php`.
- Token endpoint: `POST https://{company-subdomain}.bamboohr.com/token.php?request=token`.
- API-key requests use HTTP Basic authentication with the key as username and
  `x` as password.
- BambooHR's official Python source supports OAuth, refresh, API keys, request
  IDs, retry controls, and redacted logging. As of 2026-09-11 the documented
  `bamboohr-sdk` distribution is not discoverable on public PyPI; verify the
  registry before installing or use an approved commit pin.

## Authentication

For OAuth, register an HTTPS redirect URI, generate a high-entropy `state`, bind
it to the initiating session, and reject callbacks whose state does not match.
Exchange the code server-side. Store access token, refresh token, expiry, tenant,
subject, and granted scope in an encrypted, tenant-scoped record.

For API keys, create a dedicated BambooHR user with only required field and
workflow permissions. Store the key in the deployment secret manager. Never put
it in `.env.example`, logs, shell history, test fixtures, or a client bundle.

## Instructions

1. Identify whether the integration is partner/multi-tenant or internal/single-
   tenant, and record the authentication decision.
2. Derive the tenant subdomain from the customer's BambooHR URL; do not accept a
   full arbitrary host from untrusted input.
3. For OAuth, implement authorization-code exchange, state validation, encrypted
   token persistence, rotation, and reauthorization after terminal refresh
   failure. The SDK does not persist refreshed tokens for the application.
4. For API keys, assign a dedicated owner, document field permissions, and set a
   rotation and revocation procedure before use.
5. Test with a low-sensitivity read such as company information. Capture status
   and request ID, but discard the response body from evidence.
6. Exercise invalid-state, expired-token, revoked-key, wrong-tenant, and denied-
   field cases before production approval.

## Tool Discipline

Use Read, Glob, and Grep to inspect existing configuration and secret references.
Use Write or Edit only for approved application configuration; write placeholders,
never credentials. This skill does not authorize browser consent, credential
creation, package installation, or remote secret mutation.

## Approval Boundaries

Require explicit approval before registering an OAuth app, changing redirect
URIs, creating or rotating an API key, writing a deployment secret, or testing
against a production tenant.

## Output

Return the chosen auth mode, tenant, requested permissions, callback and token-
storage design, test evidence without bodies, key/token owner, rotation plan,
and every action still awaiting approval.

## Error Handling

- OAuth callback state mismatch: reject immediately and start a fresh flow.
- `401`: refresh once when configured; otherwise treat the credential as invalid.
- `403`: inspect the BambooHR user's field permissions; do not broaden blindly.
- Refresh failure: stop bounded retries, preserve the last valid record, and
  require reauthorization.

## Examples

- "Configure OAuth for our multi-tenant HR connector" selects OAuth and designs
  tenant-isolated token persistence.
- "Use this admin's API key in production" pauses until a dedicated least-
  privilege identity and rotation owner exist.

## Resources

Read [official evidence](references/official-docs.md) before implementation.
