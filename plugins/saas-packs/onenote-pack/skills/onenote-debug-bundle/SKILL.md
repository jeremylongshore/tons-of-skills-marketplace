---
name: onenote-debug-bundle
description: >-
  Assemble a reproducible, content-safe OneNote diagnostic bundle for engineering or Microsoft support. Use when an incident needs portable evidence. Trigger with "collect OneNote debug bundle", "redact OneNote diagnostics", or "prepare OneNote support case".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<environment> <incident-window> <operation>"
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, onenote, diagnostics]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live OneNote actions require network access, delegated authentication, and explicit approval"
---
# OneNote Redacted Diagnostic Bundle

## Overview

Assemble a reproducible, content-safe OneNote diagnostic bundle for engineering or Microsoft support.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Microsoft Graph OneNote documentation and the selected integration's tested contract.
- Named identity, content, workload, security, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures with secrets and real notebook content removed.

## Current Contract

A useful bundle separates runtime, SDK, location, delegated identity, consent, request, response, throttling, and deployment evidence. Raw notebook HTML and bearer tokens are not diagnostic defaults. Recheck the dated evidence map before relying on mutable permissions, limits, SDK behavior, supported resources, or cloud availability.

## Authentication

Record credential provenance, tenant and user aliases, granted scope names, expiry class, and a one-way fingerprint only. Never include access or refresh tokens.

## Instructions

1. Define the incident window, affected operation, data classification, audience, and retention period.
2. Collect dependency locks, sanitized configuration keys, deployment revision, and location type.
3. Capture redacted request method, route class, response status, Graph code, request identifier, latency, and retry count.
4. Scan all artifacts for tokens, secrets, user identifiers, titles, HTML bodies, and binary content.
5. Reproduce with a synthetic or read-only fixture and record observed versus expected behavior.
6. Seal the manifest with file hashes, redaction evidence, custodian, expiry, and approved transfer channel.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, delegated credentials, tenant or notebook content, consent, file transfer, deployment, writes, spend, sharing changes, or deletion.

## Approval Boundaries

Require the incident owner and data owner before collection. Require security approval before sharing externally or retaining credential metadata.

## Error Handling

- Abort if secret or page-content canaries survive redaction.
- Do not collect a whole notebook to explain one request.
- Quarantine the bundle if tenant binding or audience is unknown.

## Output

Return a minimal archive, manifest, hashes, redaction report, reproduction steps, custody log, retention expiry, and deletion owner. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Prove a synthetic 429 can be diagnosed without a token or page body.
- Reject a bundle containing a copied Authorization header.

## Validation

Exercise and record these paths with expected and observed results:

- secret canary
- content canary
- request ID
- wrong tenant
- external transfer
- expiry deletion

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal OneNote guarantee.
