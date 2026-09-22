---
name: castai-sdk-patterns
description: 'Build a production REST adapter for CAST AI from the current OpenAPI contract without inventing an unofficial SDK surface. Use when wrapping CAST AI operations in TypeScript, Python, or another service. Trigger with: "build a CAST AI client", "wrap the CAST AI API", "integrate CAST AI in code".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[adapter-or-client-root]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - kubernetes
  - cast-ai
  - api-client
  - integration
compatibility: 'Requires the current CAST AI API specification; declarative infrastructure should use the supported Terraform provider where appropriate'
---

# CAST AI Contract-First API Adapter

## Overview

Create a narrow adapter around approved CAST AI operations. Treat the OpenAPI description, regional base URL, organization scope, response schemas, and endpoint-specific rate behavior as explicit dependencies.

## Prerequisites

- Named operations and business purpose
- CAST AI region, organization boundary, and least-privilege service identity
- Current OpenAPI contract pinned or checksummed for generation
- Error, retry, telemetry, and secret-handling policy

## Instructions

### Step 1: Choose API versus Terraform

Use Read and Grep to determine whether the work is declarative infrastructure or runtime integration. Prefer the supported Terraform provider for owned desired state; use REST for bounded runtime reads or operations that the chosen provider does not own.

### Step 2: Pin the contract

Record the current API specification origin, retrieval time, checksum, selected operation IDs, and generated-client tool version. Do not copy guessed paths from examples or expose the entire generated surface to application code.

### Step 3: Build the transport boundary

Use Write or Edit to implement injected regional base URL, `X-API-Key` header handling, optional enterprise organization header, request timeout, cancellation, bounded response size, structured redaction, and correlation metadata. Never place keys in URLs or exception messages.

### Step 4: Normalize domain operations

Expose small intent-oriented methods with validated identifiers and typed results. Keep raw provider payloads behind the adapter, retain unknown fields safely, and distinguish absent data from zero values.

### Step 5: Classify failures

Map transport failures, 401, 403, 404, 409, endpoint-specific 429, 5xx, schema mismatch, deadline exhaustion, and uncertain mutation outcome. Retry only proven idempotent operations within a shared request budget.

### Step 6: Test without CAST AI

Add fixtures for every status class, regional mismatch, enterprise header omission, pagination, unknown fields, redaction, timeout, cancellation, and throttling. Keep an optional live smoke test read-only and separately protected.

## Tool Discipline

Use Read and Grep for contract and repository discovery. Use Write and Edit for the adapter, fixtures, tests, and contract receipt. This skill does not fetch credentials, call production, or claim an unofficial library is vendor-supported.

## Output

- API-versus-Terraform ownership decision
- Pinned contract receipt and selected operations
- Narrow authenticated adapter with normalized failures
- Offline contract suite and protected smoke-test boundary

## Examples

A reporting service wraps two read operations and hides generated types behind its own domain model. The same repository leaves cluster policy desired state in Terraform to avoid competing authorities.

## Error Handling

| Failure                            | Response                                            |
| ---------------------------------- | --------------------------------------------------- |
| OpenAPI operation changes          | Fail generation or contract tests for review        |
| Region and identity disagree       | Stop before sending the request                     |
| Mutation result is uncertain       | Reconcile state before retry                        |
| Response contains an unknown field | Preserve compatibility and log only its schema path |

## Resources

- [Adapter evidence and source notes](references/official-docs.md)
- [API access](https://docs.cast.ai/docs/api-access)
- [CAST AI API specification](https://api.cast.ai/spec/)
- [CAST AI API FAQ](https://docs.cast.ai/docs/api)
