---
name: adobe-debug-bundle
description: >-
  Assemble a minimal, reproducible Adobe diagnostic bundle with default-deny collection and verifiable redaction. Use for engineering or Adobe support escalation. Use when this Adobe operator workflow is needed. Trigger with "Adobe debug bundle", "collect Adobe diagnostics", or "prepare Adobe support case".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<service> <incident-window> <audience>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, diagnostics]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Redacted Diagnostic Bundle

## Overview

Assemble a minimal, reproducible Adobe diagnostic bundle with default-deny collection and verifiable redaction.. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

Useful evidence is version, configuration-key presence, service/operation, environment aliases, timestamps, status/error class, request/job/activation identifiers, retry history, and a synthetic reproduction. Tokens, secrets, signed URLs, prompts, images, documents, event bodies, and customer identifiers are excluded by default. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Use one-way fingerprints only when correlation is necessary. Never call the IMS token endpoint merely to populate a support archive.

## Instructions

1. Define incident window, service, operation, data classification, recipients, retention, and custodian.
2. Create an allowlist manifest before collection and enumerate explicitly forbidden fields and file classes.
3. Collect dependency locks, deployment revision, sanitized configuration keys, status/error evidence, and correlation IDs.
4. Reproduce with a synthetic fixture or read-only check and record expected versus observed behavior.
5. Run secret, URL, PII, document/image, prompt, and identifier canaries across every output.
6. Hash the bundle, record redactions and gaps, transfer through an approved channel, and schedule deletion.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Incident and data owners approve collection; security approves external disclosure. Any broader trace, content sample, or retention extension requires a fresh explicit approval.

## Error Handling

- Abort if an Authorization header, token, client secret, refresh token, signed URL, or customer content survives.
- Do not execute speculative network probes against production.
- Quarantine a bundle whose audience or deletion owner is unknown.

## Output

Return a minimal archive, allowlist manifest, hashes, redaction scan, reproduction, custody log, expiry, and deletion owner. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Diagnose a synthetic 429 without credential or content values.
- Reject a bundle containing a pre-signed asset URL.

## Validation

Exercise and record expected and observed results for:

- secret canary
- signed URL
- content canary
- request ID
- external transfer
- expiry deletion

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
