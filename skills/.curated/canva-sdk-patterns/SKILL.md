---
name: canva-sdk-patterns
description: 'Implement a narrow typed Canva Connect REST adapter from a pinned OpenAPI contract. Use when generating or hand-writing request types, response validation, error classification, and tenant-safe client boundaries. Trigger with: "Canva SDK pattern", "generate Canva client", "type Canva API".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[language-and-required-operations]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - client
  - operations
compatibility: 'Requires a pinned Canva OpenAPI snapshot and a backend credential/policy service; generated code is application-owned.'
---

# Canva Typed REST Adapter

## Overview

Treat the adapter as a transport boundary, not an authorization oracle or official Canva SDK. Keep policy and token rotation outside generic request methods, and tolerate documented non-breaking response additions.

## Prerequisites

- Language/runtime, package policy, and required operations
- Pinned OpenAPI bytes/checksum and generation configuration
- Authorization, token, data, retry, and test boundaries

## Instructions

### Step 1: Select the minimal surface

Use Read and Grep to list only required operations, scopes, request/response shapes, async job states, and preview flags.

### Step 2: Pin generation inputs

Store or checksum the OpenAPI contract and generator version. Review endpoint, scope, enum, validation, and preview changes before regeneration.

### Step 3: Define adapter interfaces

Use Write or Edit to expose explicit operation methods, normalized errors, response validation, timeout context, and opaque request/job metadata.

### Step 4: Keep policy outside

Require an already-authorized tenant/resource decision and token lease. Do not let a generic client select roles, broaden scopes, refresh concurrently, or log bodies.

### Step 5: Handle responses safely

Validate required fields, accept additive unknown fields where the contract allows, reject unsafe type/status drift, and model in-progress/success/failed without exhaustive assumptions about preview enums.

### Step 6: Constrain retries

Retry only classified safe reads or reconciled operations under a bounded policy. Return authorization and throttling facts to their owning layers.

### Step 7: Test contract drift

Exercise fixtures for success, provider errors, unknown fields, changed enums, malformed bodies, timeouts, duplicate prevention, and redaction.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

A generated TypeScript transport covers users, designs, and exports, but an application service still owns tenant authorization, refresh serialization, operation identity, and result retention.

## Error Handling

| Failure | Response |
| --- | --- |
| Generated diff changes scopes | Require authorization and consent review |
| Client auto-retries writes | Disable it and add operation reconciliation |
| Unknown response field breaks parsing | Adopt additive-safe validation where permitted |
| Adapter logs bodies or tokens | Block release and remediate |

## Resources

- [First-party source notes](references/official-docs.md)
- [Latest OpenAPI](https://www.canva.dev/sources/connect/api/latest/api.yml)
- [Starter Kit](https://github.com/canva-sdks/canva-connect-api-starter-kit)
