---
name: canva-local-dev-loop
description: 'Configure local Canva Connect development with contract fixtures and an optional dedicated OAuth integration. Use when building adapters, callbacks, async-job handling, or UI flows without using production credentials. Trigger with: "Canva local setup", "mock Canva API", "test Canva callback locally".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[project-path-and-test-mode]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - development
  - operations
compatibility: 'Live local OAuth requires a dedicated development integration, controlled redirect URI, test user, and encrypted or ephemeral backend token store.'
---

# Canva Mock-First Local Loop

## Overview

Make the default loop offline, deterministic, and safe. A live development check is exceptional and must not reuse production integrations, tokens, assets, or redirect configuration.

## Prerequisites

- Existing project, package manager, and test framework
- Pinned OpenAPI/fixture version and adapter boundary
- Dedicated development integration and synthetic-user policy if live mode is approved

## Instructions

### Step 1: Inventory the project

Use Read and Grep to locate HTTP adapters, OAuth callback/state handling, fixtures, environment loading, token persistence, async job polling, and ignored files.

### Step 2: Create contract fixtures

Use Write or Edit to model identity, designs, exports, assets, autofill, errors, throttling, and unknown fields at the transport boundary.

### Step 3: Keep credentials out by default

Make tests fail if production-looking secrets are loaded. Never save tokens in a plaintext project file, browser storage, snapshot, or console.

### Step 4: Test callback state

Exercise success, denial, state mismatch, expired/replayed callback, missing verifier, token-exchange failure, and atomic refresh replacement without real secrets.

### Step 5: Test async reconciliation

Use deterministic clocks to cover in-progress, success, failed, timeout, retry, restart, and duplicate-delivery behavior.

### Step 6: Run one approved live read

If required, use a dedicated development integration and test user for a non-mutating request, then delete ephemeral credentials and evidence under policy.

### Step 7: Close production drift

Document every development redirect URI and remove localhost, loopback, and tunnel hosts before production review.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

A developer runs fixtures for OAuth and export polling on every change. Once, a dedicated dev user performs a read-only connection proof; no token is written to the repository or browser.

## Error Handling

| Failure | Response |
| --- | --- |
| Production credential detected | Abort and rotate through the owner |
| Fixture diverges from OpenAPI | Update it in a reviewed contract change |
| Tunnel host reaches production config | Remove it before release |
| Live test creates real content | Stop and clean it under the approved policy |

## Resources

- [First-party source notes](references/official-docs.md)
- [Quickstart](https://www.canva.dev/docs/connect/quickstart/)
- [Starter Kit](https://github.com/canva-sdks/canva-connect-api-starter-kit)
