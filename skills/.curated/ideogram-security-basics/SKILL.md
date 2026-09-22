---
name: ideogram-security-basics
description: >-
  Harden an Ideogram integration across credentials, untrusted media, content safety, copyright controls, storage, and tenant authorization. Use when reviewing a threat model or implementing security controls. Trigger with "secure Ideogram", "audit Ideogram image uploads", or "review Ideogram content safety".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<application-boundary> <data-class> <environment>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, security]
model: inherit
effort: high
compatibility: "Designed for Claude Code; security review defaults to repository and fixture evidence"
---
# Ideogram Security Boundary

## Overview

Threat-model the full image lifecycle rather than only the API key. Protect server-side authority, uploaded bytes, prompt and structured-description content, safety decisions, copyright settings, temporary vendor URLs, durable assets, and cross-tenant access.

## Prerequisites

- Data classification, tenant model, rights policy, moderation owner, and retention schedule.
- Architecture showing upload, API, queue, webhook, download, storage, and publishing boundaries.
- Incident paths for credential exposure, unsafe output, malicious media, and unauthorized asset access.

## Current Contract

Ideogram uses a server-side `Api-Key`. Returned items expose `is_image_safe`; unsafe items can have an empty URL. V4 supports `enable_copyright_detection`, and request plus organization settings combine as an OR gate. Generated URLs expire and must not become the application's authorization layer.

## Authentication

Store `IDEOGRAM_API_KEY` in a managed secret store and send it only to `https://api.ideogram.ai`. Authenticate application users separately, authorize each operation and object by tenant, and issue application-owned short-lived download access after durable storage.

## Instructions

1. Map every trust boundary and classify keys, prompts, structured prompts, uploads, masks, generated assets, metadata, and logs.
2. Keep paid API calls behind a server-side policy enforcement point with tenant authentication, authorization, budgets, and rate controls.
3. Validate media signatures, types, dimensions, byte limits, decompression behavior, and malware policy before forwarding.
4. Apply rights, content-safety, and copyright-detection policy before generation and again before publication.
5. Check `is_image_safe`, validate download type and size, store under opaque tenant-scoped keys, and discard vendor URLs.
6. Encrypt retained objects, restrict service identities, log content-free decisions, and enforce deletion.
7. Test key rotation, unsafe output, cross-tenant denial, malicious upload, expired URL, and object deletion.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, policies, infrastructure, and fixtures. Use Write and Edit for approved hardening and tests. Do not open customer media, rotate production keys, weaken policy, or run live generation without authority.

## Approval Boundaries

Require accountable approval for sensitive-image processing, copyright-control changes, external publication, retention exceptions, identity or role changes, key rotation, and production rollout. Fail closed when rights or tenant ownership is ambiguous.

## Error Handling

- Revoke and rotate an exposed key; deleting a log line alone is insufficient.
- Treat unsafe output as a policy result and never auto-rewrite prompts to bypass it.
- Reject redirects, unexpected media types, oversized bodies, and storage keys outside the authorized tenant prefix.

## Output

Return boundaries reviewed, controls present or missing, risk severity, evidence locations, tests, owners, remediation, deployment state, and rollback. Exclude credentials, content, URLs, and exploitable secret locations.

## Examples

- Deny a browser request that attempts to call Ideogram directly with a shared key.
- Persist an approved image to a tenant-owned object key and expose only an application-signed download.

## Validation

Run secret scanning, authorization tests, media parser fixtures, safety branches, storage isolation, deletion, and key-rotation rehearsal. Confirm logs and traces contain no key, prompt, URL, or binary content.

## Resources

- [Current first-party evidence map](references/official-docs.md) — use the dated endpoint, webhook, billing, team, and training links as the contract index for this workflow.
- Recheck the endpoint-specific page and current OpenAPI description before relying on an enum, limit, beta feature, or lifecycle claim.
- Record live observations as environment-specific evidence, not as universal vendor guarantees.
