---
name: assemblyai-local-dev-loop
description: >-
  Build an AssemblyAI local loop with synthetic fixtures, recorded contracts, and an optional bounded live lane. Use when developing without exposing audio or uncontrolled credits. Trigger with "AssemblyAI local dev" or "mock AssemblyAI".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, assemblyai]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live AssemblyAI work requires network access"
---
# AssemblyAI Deterministic Local Development

## Overview

Build an AssemblyAI local loop with synthetic fixtures, recorded contracts, and an optional bounded live lane. Treat live audio, transcript content, credentials, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The AssemblyAI project, environment, region, data classification, and accountable owner.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Ordinary development stays offline. Fixtures model REST job states, Streaming v3 messages, both webhook families, LLM Gateway outputs, throttling, duplicates, and termination. A public tunnel and live API call are explicit exposure and cost boundaries.

## Authentication

For live work, inject `ASSEMBLYAI_API_KEY` from an approved secret manager and send the raw value only in the AssemblyAI `Authorization` header to the configured first-party host. Never print, commit, place in a URL, or expose it to an untrusted client. Callback secrets and temporary streaming tokens are separate credentials.

## Instructions

1. Map the adapter surfaces actually used.
2. Create synthetic audio and content-free response fixtures.
3. Inject a fake clock, deterministic jitter, and bounded queues.
4. Cover delayed polling, 429, duplicates, malformed events, and disconnects.
5. Protect live tests behind a separate flag and secret context.
6. Review recorded-contract diffs against current first-party schemas.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call AssemblyAI, upload audio, open a streaming session, mint a token, replay a callback, deploy, rotate a key, or delete a transcript merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live audio processing, production credential or endpoint changes, paid model or capacity changes, content retention, callback replay, deployment, or deletion. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- A default test that needs a live key is not deterministic.
- Real transcript text does not belong in golden fixtures.
- A tunnel must be authenticated, disposable, and explicitly approved.

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
