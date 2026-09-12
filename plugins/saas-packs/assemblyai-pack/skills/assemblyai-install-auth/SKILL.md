---
name: assemblyai-install-auth
description: >-
  Configure AssemblyAI keys, regional endpoints, and server-versus-browser authentication safely. Use when installing or authenticating an integration. Trigger with "AssemblyAI auth", "AssemblyAI API key", or "AssemblyAI endpoint setup".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <region> <runtime>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, assemblyai]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live AssemblyAI work requires network access"
---
# AssemblyAI Identity and Endpoint Setup

## Overview

Configure AssemblyAI keys, regional endpoints, and server-versus-browser authentication safely. Treat live audio, transcript content, credentials, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The AssemblyAI project, environment, region, data classification, and accountable owner.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Pre-recorded REST uses the approved US or EU `api.assemblyai.com` host and the raw project key in the `Authorization` header. Streaming uses the v3 WebSocket host. Browser and mobile clients receive short-lived, single-use streaming tokens from a trusted backend; they never receive the project key.

## Authentication

For live work, inject `ASSEMBLYAI_API_KEY` from an approved secret manager and send the raw value only in the AssemblyAI `Authorization` header to the configured first-party host. Never print, commit, place in a URL, or expose it to an untrusted client. Callback secrets and temporary streaming tokens are separate credentials.

## Instructions

1. Inventory runtime trust, data class, region, and environment.
2. Pin the official SDK and centralize reviewed endpoint configuration.
3. Separate keys by environment and inject them from the secret manager.
4. Design an authorized, origin-limited token endpoint for untrusted clients.
5. Verify one synthetic pre-recorded request with explicit `speech_models`.
6. Record host, key-owner, rotation, token TTL, and redacted results.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call AssemblyAI, upload audio, open a streaming session, mint a token, replay a callback, deploy, rotate a key, or delete a transcript merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live audio processing, production credential or endpoint changes, paid model or capacity changes, content retention, callback replay, deployment, or deletion. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Wrong-region traffic is a residency incident, not a retry.
- A project key in browser code is compromised and must be rotated.
- Do not add an undocumented Bearer scheme to the REST authorization value.

## Output

Return the operation scope, environment, region, contract surface, authorization class, model and feature decisions, deterministic validation results, content-free identifiers, risks, cleanup or rollback state, and a concise pass/fail receipt. Exclude credentials, signed URLs, audio, transcript text, prompts, and customer-derived content.

## Example

- Start with the named environment, approved regional host, synthetic fixture identity, and bounded operation budget.
- Finish with safe IDs, contract and assertion counts, terminal state, cleanup status, and the decision owner; never reproduce speech content.

## Validation

Rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm rollback, termination, or deletion state before reporting success.

## References

Review the dated first-party evidence map before relying on any model, parameter, limit, price, region, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
