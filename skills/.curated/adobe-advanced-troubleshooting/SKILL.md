---
name: adobe-advanced-troubleshooting
description: >-
  Isolate complex Adobe failures across DNS/TLS, auth, entitlement, schema, async state, storage, Runtime, and downstream layers without leaking credentials or content. Use when the task requires adobe layered failure isolation. Trigger with "deep debug Adobe", "Adobe job stuck", or "Adobe intermittent failure".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<service> <operation> <incident-evidence>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, troubleshooting]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Layered Failure Isolation

## Overview

Isolate complex Adobe failures across DNS/TLS, auth, entitlement, schema, async state, storage, Runtime, and downstream layers without leaking credentials or content. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

Troubleshooting proceeds from sanitized wire facts and known control boundaries. Decoding a bearer token locally is not authoritative proof of entitlement and raw verbose traces are unsafe defaults; use token response metadata, Console assignments, and request/job IDs. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Collect aliases, scope/profile names, expiry class, last rotation/use evidence, and correlation IDs. Never expose token payloads, Authorization, signed URLs, prompts, documents, images, or event bodies.

## Instructions

1. Freeze speculative retries and capture one redacted failure envelope, topology, time window, and expected contract.
2. Check DNS/TLS/egress and service status without sending customer data or credentials to unapproved tools.
3. Verify credential type, organization/project/workspace, entitlement, scopes, profiles, host, method, version, and schema.
4. Trace submission, returned status URL, polling, terminal state, storage access, webhook/activation, and downstream acknowledgement.
5. Compare a synthetic control and the failing path one layer at a time while preserving request/job/activation IDs.
6. State the isolated layer, falsified hypotheses, minimal remediation, verification, and Adobe escalation evidence.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Incident/data/security owners approve production diagnostics. Any token introspection, content sample, external support upload, replay, cancellation, or deletion needs explicit approval.

## Error Handling

- Do not paste a token into an online decoder.
- Do not run curl -v with secrets into shared logs.
- Do not create new jobs while the original completion state is unknown.

## Output

Return the layer map, redacted evidence, hypotheses/tests, isolated fault, smallest fix, verification, and escalation packet. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Differentiate storage URL expiry from Adobe job failure.
- Differentiate missing product profile from malformed OAuth request.

## Validation

Exercise and record expected and observed results for:

- network
- auth
- entitlement
- schema
- unknown job
- downstream

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
