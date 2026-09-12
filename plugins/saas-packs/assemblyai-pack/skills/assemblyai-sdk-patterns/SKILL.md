---
name: assemblyai-sdk-patterns
description: >-
  Analyze and design a typed AssemblyAI adapter that isolates SDK drift, regional routing, polling, and streaming lifecycles. Use when integrating an official SDK. Trigger with "AssemblyAI SDK pattern", "AssemblyAI adapter", or "wrap AssemblyAI".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <language> <runtime>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, assemblyai]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live AssemblyAI work requires network access"
---
# AssemblyAI Typed Adapter Boundary

## Overview

Design a narrow application-owned boundary around the current SDK. Keep data, credentials, region, retries, spend, and destructive state separately governed.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The AssemblyAI project, environment, region, data classification, and accountable owner.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Pre-recorded jobs, Streaming v3 sessions, temporary-token issuance, webhooks, and LLM Gateway requests have different lifecycles. Keep vendor objects behind a narrow application-owned port. New code must not expose legacy LeMUR methods or Streaming v2 service names.

## Authentication

For live work, inject `ASSEMBLYAI_API_KEY` from an approved secret manager and send the raw value only in the AssemblyAI `Authorization` header to the configured first-party host. Never print, commit, place in a URL, or expose it to an untrusted client. Callback secrets and temporary streaming tokens are separate credentials.

## Instructions

1. Inventory direct SDK imports and classify each surface.
2. Define narrow request, result, and stable application-error types.
3. Centralize immutable region, authentication, deadlines, and retry policy.
4. Separate job submission from completion retrieval.
5. Model streaming connect, begin, turns, termination, and confirmation.
6. Pin the SDK and prove the boundary with contract fixtures.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call AssemblyAI, upload audio, open a streaming session, mint a token, replay a callback, deploy, rotate a key, or delete a transcript merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live audio processing, production credential or endpoint changes, paid model or capacity changes, content retention, callback replay, deployment, or deletion. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Mutable tenant state in a singleton can cross-contaminate requests.
- Catch-all retries can duplicate billed work.
- Vendor response objects crossing service boundaries make upgrades unsafe.

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
