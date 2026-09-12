---
name: adobe-hello-world
description: >-
  Prove one Adobe API connection with a current, read-only or synthetic operation and a content-safe receipt. Use during onboarding before any production workflow. Use when this Adobe operator workflow is needed. Trigger with "Adobe hello world", "test Adobe connection", or "verify Adobe entitlement".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<product-api> <sandbox> <proof-operation>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, onboarding]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Minimal Access Proof

## Overview

Prove one Adobe API connection with a current, read-only or synthetic operation and a content-safe receipt.. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

The smallest useful proof is product-specific: token acquisition alone does not demonstrate API entitlement. Prefer a documented read or a synthetic asynchronous job whose artifact can be safely deleted; do not use retired Photoshop v1, /sensei/cutout, or Lightroom Firefly Services endpoints. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Use a dedicated non-production credential or consenting test user and record only aliases, scope names, product profiles, response status, and request identifiers.

## Instructions

1. Resolve the exact Adobe organization, project, workspace, credential type, and service.
2. Read the current product quickstart and identify the least consequential documented proof.
3. Validate endpoint host, method, request schema, scopes, entitlement, and storage requirements offline.
4. Run exactly one bounded proof and capture redacted response and correlation evidence.
5. Verify the expected allow case and one safe denied or invalid fixture without broadening access.
6. Delete approved temporary assets and issue a pass, fail, or entitlement-blocked result.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Require the sandbox and data owners before a live call. Image/document generation, upload, spend, or asset deletion needs explicit approval even in a test environment.

## Error Handling

- Stop if the service is absent from Developer Console.
- Do not treat a 401, 403, or policy rejection as a reason to guess new scopes.
- Never use production customer files as a hello-world fixture.

## Output

Return the selected proof, current documentation, auth/entitlement aliases, request receipt, negative result, cleanup evidence, and decision. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Verify one authorized synthetic request without exposing the bearer token.
- Demonstrate that a retired endpoint is rejected by the preflight.

## Validation

Exercise and record expected and observed results for:

- valid proof
- missing entitlement
- wrong host
- invalid fixture
- timeout
- cleanup

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
