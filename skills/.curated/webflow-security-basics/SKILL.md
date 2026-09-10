---
name: webflow-security-basics
description: >-
  Harden Webflow tokens, scopes, webhook verification, logs, and live-write boundaries. Use when threat-modeling an integration or preparing it for production. Trigger with "secure Webflow", "verify Webflow webhook", or "audit Webflow token".
argument-hint: "[project-path] [site-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- security
- webhooks
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow Integration Security

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- Choose site token, read-only workspace token, or OAuth by integration type; do not emulate multi-tenancy by sharing one broad token.
- Site tokens have scope and endpoint limits, expire after 365 inactive days, and should be revoked immediately when compromised.
- API-created webhooks include `x-webflow-timestamp` and `x-webflow-signature`; dashboard-created webhooks do not include the headers needed for signature validation.
- Signing keys differ: qualifying site-token webhooks receive a webhook secret, while OAuth-created webhooks use the OAuth app client secret. Webflow recommends SDK verification.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Map data flows, token holders, sites, webhook destinations, log stores, CI, and every create/update/delete/publish path.
2. Build an endpoint-to-scope table and remove scopes that no current path requires.
3. Keep secrets server-side in a managed store; block authorization headers and sensitive webhook payloads from logs and traces.
4. For signed webhooks, preserve the request representation expected by the official verifier, validate signature and timestamp, and reject replays older than five minutes.
5. Require target identity, preview or diff, explicit approval, and post-write verification for live mutations.
6. Document revocation, rotation, incident ownership, and how to invalidate downstream sessions without exposing replacement values.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| Dashboard webhook lacks signature | Recreate through the API if signature verification is required; do not invent a shared secret. |
| Signature mismatch | Reject the request and inspect body serialization, timestamp, and the correct signing key. |
| Token exposed | Revoke it, rotate affected integrations, and scrub retained logs through the approved incident process. |

## Examples

For a public Data Client app, request only endpoint-derived OAuth scopes, store client secrets server-side, create webhooks through the API, use the SDK verifier, enforce the five-minute timestamp window, and redact form data.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
