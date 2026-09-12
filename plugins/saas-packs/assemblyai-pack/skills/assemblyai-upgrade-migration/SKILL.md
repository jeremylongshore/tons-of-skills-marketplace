---
name: assemblyai-upgrade-migration
description: >-
  Migrate legacy AssemblyAI Streaming v2 and LeMUR integrations to Streaming v3 and LLM Gateway with parity evidence. Use when removing deprecated contracts. Trigger with "migrate AssemblyAI", "LeMUR migration", or "Streaming v3 upgrade".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <legacy-surface>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, assemblyai]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live AssemblyAI work requires network access"
---
# AssemblyAI v3 and LLM Gateway Migration

## Overview

Migrate legacy AssemblyAI Streaming v2 and LeMUR integrations to Streaming v3 and LLM Gateway with parity evidence. Treat live audio, transcript content, credentials, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The AssemblyAI project, environment, region, data classification, and accountable owner.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Streaming v2 used `/v2/realtime/ws`; v3 uses `/v3/ws` with different messages, turns, configuration, and termination. LeMUR sunset on March 31, 2026; LLM Gateway is the current analysis path. Deprecated transcript summary parameters must not anchor new designs.

## Authentication

For live work, inject `ASSEMBLYAI_API_KEY` from an approved secret manager and send the raw value only in the AssemblyAI `Authorization` header to the configured first-party host. Never print, commit, place in a URL, or expose it to an untrusted client. Callback secrets and temporary streaming tokens are separate credentials.

## Instructions

1. Inventory endpoints, SDK methods, handlers, fixtures, dashboards, and legacy credentials.
2. Capture approved legacy behavior with synthetic golden cases.
3. Map v2 messages and shutdown to v3 begin, turns, configuration, and termination.
4. Map LeMUR prompts and outputs to schema-constrained LLM Gateway requests.
5. Compare quality, latency, structured results, privacy, and cost.
6. Canary the new route, test rollback, then remove legacy code and secrets.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call AssemblyAI, upload audio, open a streaming session, mint a token, replay a callback, deploy, rotate a key, or delete a transcript merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live audio processing, production credential or endpoint changes, paid model or capacity changes, content retention, callback replay, deployment, or deletion. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Changing only the WebSocket URL leaves v2 handlers broken.
- LeMUR calls after sunset are a hard migration defect.
- LLM parity needs semantic and schema assertions, not byte equality.

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
