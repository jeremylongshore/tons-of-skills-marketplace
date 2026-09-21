---
name: runway-install-auth
description: >-
  Install and verify a server-side Runway Dev client without spending generation credits or exposing an organization key. Use when bootstrapping or rotating an integration. Trigger with: "configure Runway API", "install Runway SDK", "verify Runway authentication".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[node|python|rest]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - runway
  - authentication
  - sdk
  - secrets
compatibility: 'Requires server-side Runway Dev access, current first-party documentation, an approved credit budget, and controlled media storage.'
---

# Secure Runway SDK and REST Bootstrap

## Overview

Establish a reproducible client, explicit API-version contract, and non-billable authentication probe. Runway API keys are organization-scoped credentials, so a working client is not evidence that a user should retain access or that a billable generation is approved.

## Prerequisites

- Runway Dev organization and an operator authorized to manage API keys
- Node.js 18+ or Python 3.8+, or an HTTP client for the REST path
- A secret manager and a reviewed `X-Runway-Version` value

## Instructions

### Step 1: Discover the integration boundary

Use Read and Grep to locate runtime manifests, lockfiles, existing Runway clients, environment-variable names, and browser/server boundaries. Separate Runway Dev API access from the consumer Runway web application and from the OAuth-based Runway Dev MCP.

### Step 2: Resolve and pin the client

Choose `@runwayml/sdk`, `runwayml`, or direct REST. Query the package registry and official SDK page at implementation time, review the changelog, and pin the selected compatible version in the project lockfile instead of copying a stale version from this skill.

### Step 3: Provision the key safely

Create or rotate a key in the Developer Portal under the intended organization. Store it as `RUNWAYML_API_SECRET` in the deployment secret manager. Never place it in source, logs, screenshots, browser bundles, MCP configuration, or client-visible environment variables.

### Step 4: Configure the protocol

The official SDKs read `RUNWAYML_API_SECRET` and supply the version header. For direct HTTP, send `Authorization: Bearer <secret>` and `X-Runway-Version: 2024-11-06` to `https://api.dev.runwayml.com`; centralize both headers in one server-side client.

### Step 5: Run a read-only probe

Use a documented organization or task read endpoint that the key is authorized to access. Record status, request ID, API version, and organization identity in redacted form. Do not create a generation merely to prove authentication.

### Step 6: Exercise rotation and revocation

Install the replacement key, prove the read path, switch consumers, disable the old key explicitly, and prove the old key receives `401`. Removing an organization member alone does not revoke an organization-scoped key.

## Authentication

Runway REST authentication is a bearer API secret plus the required `X-Runway-Version` header. The SDKs obtain the secret from `RUNWAYML_API_SECRET`; browser code must call a protected server endpoint rather than receive the secret.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, lockfiles, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, cancel, delete, retry, deploy, rotate, revoke, publish, or otherwise mutate production Runway resources without explicit operator approval.

## Output

- Pinned SDK or reviewed REST-client decision
- Redacted authentication probe with organization and API-version evidence
- Key rotation, revocation, and rollback record

Return the environment, organization alias, operation and task identifiers, API and SDK versions, model or router policy, source-contract fingerprint, task-state evidence, credit boundary, output disposition, unresolved risk, rollback state, and final decision without exposing API secrets, prompt or media contents, or temporary signed URLs.

## Examples

A service replaces an exposed development key. The operator loads a new secret version, proves a read-only organization call, shifts one canary worker, disables the old key, and confirms that the disabled credential fails without issuing a paid generation.

## Error Handling

| Failure | Response |
| --- | --- |
| 401 from the probe | Check the complete key, organization, disabled state, bearer header, and secret-manager mapping; do not retry blindly. |
| Version-header rejection | Compare the reviewed official version contract and the actual outgoing request; update one central client. |
| Key appears in a client bundle or log | Stop rollout, revoke it, purge accessible artifacts through the approved process, and issue a replacement. |

## Validation

Verify the resolved dependency, lockfile, server-only secret boundary, outgoing host and headers, a successful read-only probe, and a failed-old-key rotation test. Do not report success from environment-variable presence alone.

## Resources

- [First-party source notes](references/official-docs.md)
- [Runway agent context](https://docs.dev.runwayml.com/ai-context.md)
- [API reference](https://docs.dev.runwayml.com/api.md)
- [Models](https://docs.dev.runwayml.com/guides/models.md)
- [Usage tiers](https://docs.dev.runwayml.com/usage/tiers.md)
- [Pricing](https://docs.dev.runwayml.com/guides/pricing.md)
- [Production checklist](https://docs.dev.runwayml.com/guides/go-live.md)
