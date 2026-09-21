---
name: assemblyai-core-workflow-b
description: >-
  Analyze and operate an AssemblyAI Streaming v3 session with safe tokens, audio framing, turn handling, and explicit termination. Use when building live captions or voice agents. Trigger with "AssemblyAI streaming", "AssemblyAI v3 WebSocket", or "live transcript".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<runtime> <speech-model> <sample-rate>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, assemblyai]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live AssemblyAI work requires network access"
---
# AssemblyAI Streaming v3 Session

## Overview

Operate live transcription around the current v3 message and billing lifecycle. Govern capture, credentials, finalized content, reconnects, and termination separately.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The AssemblyAI project, environment, region, data classification, and accountable owner.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Use `wss://streaming.assemblyai.com/v3/ws` or the approved residency host. Handle `Begin`, partial and finalized `Turn` messages, and `Termination`. Match encoding and sample rate, pace audio correctly, use backend-minted tokens in untrusted clients, and terminate explicitly so abandoned connections do not continue billing.

## Authentication

For live work, inject `ASSEMBLYAI_API_KEY` from an approved secret manager and send the raw value only in the AssemblyAI `Authorization` header to the configured first-party host. Never print, commit, place in a URL, or expose it to an untrusted client. Callback secrets and temporary streaming tokens are separate credentials.

## Instructions

1. Confirm live-capture consent, region, model, encoding, and turn policy.
2. Mint a short-lived single-use token for untrusted clients.
3. Verify `Begin` before sending correctly paced audio frames.
4. Order turns and persist only approved finalized content.
5. Treat reconnect as a new governed session boundary.
6. Send termination, await confirmation, stop capture, and record duration.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call AssemblyAI, upload audio, open a streaming session, mint a token, replay a callback, deploy, rotate a key, or delete a transcript merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live audio processing, production credential or endpoint changes, paid model or capacity changes, content retention, callback replay, deployment, or deletion. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- The `/v2/realtime/ws` route is legacy and must migrate.
- Encoding or sample-rate mismatch is not repaired by retries.
- Missing termination evidence leaves cost and completeness uncertain.

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
