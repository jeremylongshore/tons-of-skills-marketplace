---
name: assemblyai-debug-bundle
description: >-
  Produce a redacted AssemblyAI diagnostic bundle for support and incident triage. Use when evidence is needed without exposing keys, URLs, audio, transcripts, or prompts. Trigger with "AssemblyAI debug bundle" or "support evidence".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<incident-id> <environment> <time-window>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, assemblyai]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live AssemblyAI work requires network access"
---
# AssemblyAI Privacy-safe Diagnostic Bundle

## Overview

Produce a redacted AssemblyAI diagnostic bundle for support and incident triage. Treat live audio, transcript content, credentials, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The AssemblyAI project, environment, region, data classification, and accountable owner.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Allowlisted evidence includes hosts, SDK version, operation, models, hashed IDs, status transitions, timestamps, durations, response or close codes, delivery attempts, and termination state. Exclude authorization values, signed URLs, token responses, audio, transcript text, prompts, and full callback bodies by default.

## Authentication

For live work, inject `ASSEMBLYAI_API_KEY` from an approved secret manager and send the raw value only in the AssemblyAI `Authorization` header to the configured first-party host. Never print, commit, place in a URL, or expose it to an untrusted client. Callback secrets and temporary streaming tokens are separate credentials.

## Instructions

1. Define incident scope, audience, region, and evidence expiry.
2. Inventory logs before copying and label content-bearing fields.
3. Extract only allowlisted metadata and hash stable identifiers when useful.
4. Replace every secret or content field with a fixed marker.
5. Scan the staged bundle for secrets and speech-derived content.
6. Obtain review, transfer securely, and record destruction date.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call AssemblyAI, upload audio, open a streaming session, mint a token, replay a callback, deploy, rotate a key, or delete a transcript merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live audio processing, production credential or endpoint changes, paid model or capacity changes, content retention, callback replay, deployment, or deletion. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Recursive environment dumps collect unrelated secrets.
- Full vendor responses remain sensitive after key removal.
- Hashing low-entropy personal values is not anonymization.

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
