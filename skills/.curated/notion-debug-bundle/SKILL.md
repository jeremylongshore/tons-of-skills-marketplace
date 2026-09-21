---
name: notion-debug-bundle
description: >-
  Assemble a reproducible, secret-free Notion integration diagnostic bundle for engineering or support. Use when an incident needs portable evidence. Trigger with "collect Notion debug bundle", "redact Notion diagnostics", or "prepare Notion support case".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<environment> <incident-window> <operation>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, diagnostics]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Redacted Debug Bundle

## Overview

Assemble a reproducible, secret-free Notion integration diagnostic bundle for engineering or support.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Useful evidence includes dependency versions, selected API version, operation names, status and error codes, request identifiers, timings, retry decisions, and content-free object fingerprints. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Never collect bearer values, OAuth secrets, verification tokens, cookies, page content, user email, file URLs, or full request and response bodies by default.

## Instructions

1. Define the incident window, affected operation, environment, tenant alias, and bundle recipient.
2. Collect dependency locks, redacted configuration keys, selected version, and runtime metadata.
3. Collect status, structured error code, request identifier, latency, retry count, and object-type fingerprints.
4. Run deterministic redaction and secret scanning over the staged bundle.
5. Generate a manifest with hashes, exclusions, collector version, and custody owner.
6. Review the final archive manually before approved transfer.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require the incident commander and data owner before collecting response excerpts or transmitting a bundle outside the approved boundary.

## Error Handling

- Abort packaging if any secret pattern or raw content remains.
- A token prefix is still credential material; store only a one-way fingerprint.
- Do not broaden collection to unrelated tenants.

## Output

Return the bundle manifest, hashes, redaction report, explicit exclusions, collection gaps, retention deadline, and transfer approval. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Package a 429 incident using timings and request IDs without page bodies.
- Prepare a vendor escalation with one approved redacted error envelope.

## Validation

Exercise and record these paths with expected and observed results:

- secret canaries
- content canaries
- tenant boundary
- hash reproducibility
- manual review
- retention expiry

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
