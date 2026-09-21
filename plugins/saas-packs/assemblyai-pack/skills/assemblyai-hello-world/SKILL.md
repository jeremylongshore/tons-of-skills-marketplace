---
name: assemblyai-hello-world
description: >-
  Run a bounded AssemblyAI pre-recorded smoke test with explicit model fallback and safe output. Use when proving a new integration. Trigger with "AssemblyAI hello world", "first AssemblyAI transcript", or "AssemblyAI smoke test".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<fixture-url-or-path> <region>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, assemblyai]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live AssemblyAI work requires network access"
---
# AssemblyAI Pre-recorded Smoke Test

## Overview

Run a bounded AssemblyAI pre-recorded smoke test with explicit model fallback and safe output. Treat live audio, transcript content, credentials, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The AssemblyAI project, environment, region, data classification, and accountable owner.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Current pre-recorded requests require an explicit `speech_models` list; there is no default. Submit a consented fixture, keep its transcript ID as the job handle, and require a completed terminal state plus content-safe assertions before declaring success.

## Authentication

For live work, inject `ASSEMBLYAI_API_KEY` from an approved secret manager and send the raw value only in the AssemblyAI `Authorization` header to the configured first-party host. Never print, commit, place in a URL, or expose it to an untrusted client. Callback secrets and temporary streaming tokens are separate credentials.

## Instructions

1. Checksum a short synthetic fixture and record expected language.
2. Choose the regional host and supported ordered model list.
3. Submit once without logging keys or signed source URLs.
4. Poll with a deadline or consume an authenticated callback.
5. Verify status, plausible duration, selected model, and an expected phrase.
6. Delete the fixture transcript after the evidence window.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call AssemblyAI, upload audio, open a streaming session, mint a token, replay a callback, deploy, rotate a key, or delete a transcript merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live audio processing, production credential or endpoint changes, paid model or capacity changes, content retention, callback replay, deployment, or deletion. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- HTTP success proves submission, not successful transcription.
- An inaccessible private URL needs an authorized delivery path, not public exposure.
- Empty or implausible output fails the smoke test.

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
