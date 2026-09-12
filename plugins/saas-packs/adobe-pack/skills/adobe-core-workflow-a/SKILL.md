---
name: adobe-core-workflow-a
description: >-
  Run a current Adobe Firefly image generation job with prompt approval, response-led polling, artifact custody, and cancellation. Use for approved creative automation. Use when this Adobe operator workflow is needed. Trigger with "generate with Firefly", "Firefly async job", or "Adobe image generation".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<approved-prompt> <model-operation> <output-destination>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, firefly]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Firefly Controlled Async Generation

## Overview

Run a current Adobe Firefly image generation job with prompt approval, response-led polling, artifact custody, and cancellation.. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

Current Firefly asynchronous operations return jobId, statusUrl, and cancelUrl. Follow those returned URLs rather than inventing a jobs route. Model/API versions and supported input-storage domains are mutable; recheck usage notes for the selected operation. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Acquire OAuth Server-to-Server credentials only after enterprise entitlement and product assignment are proven. Send x-api-key and bearer headers server-side; never expose them to a browser or job record.

## Instructions

1. Record the approved business purpose, prompt, model/operation, dimensions, quantity, budget, and content owner.
2. Read the current API and usage notes; validate endpoint version, request schema, supported signed-URL hosts, and content rules.
3. Create a redacted idempotency record and submit one bounded asynchronous job.
4. Persist jobId plus returned statusUrl and cancelUrl, then poll with jitter and strict elapsed-time limits.
5. On success, validate media type and size, transfer the artifact to approved storage, and preserve provenance/content-credential metadata.
6. On failure or timeout, classify the vendor response, cancel when approved, reconcile spend, and expire temporary access.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Require creative and budget approval before submission. External storage, personal/regulated content, bulk generation, cancellation, publication, and deletion each require the named owner.

## Error Handling

- Never retry a policy or validation rejection by silently rewriting the prompt.
- After ambiguous submission, reconcile by idempotency evidence before resubmitting.
- Stop if a returned URL leaves the documented allowlist or includes a secret in logs.

## Output

Return prompt and policy receipt, version/operation evidence, job ledger, polling history, artifact hash/location, provenance, spend class, and cleanup. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Complete a synthetic async job by following returned URLs.
- Cancel a sandbox job after the polling budget expires.

## Validation

Exercise and record expected and observed results for:

- success
- policy rejection
- 429
- unknown status
- timeout/cancel
- artifact validation

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
