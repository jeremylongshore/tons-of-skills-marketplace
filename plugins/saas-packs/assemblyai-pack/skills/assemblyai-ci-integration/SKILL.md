---
name: assemblyai-ci-integration
description: >-
  Build AssemblyAI CI with offline REST, Streaming v3, webhook, gateway, secret, and lifecycle tests plus a tightly gated live lane. Use when adding automated verification. Trigger with "AssemblyAI CI" or "contract test".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, assemblyai]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live AssemblyAI work requires network access"
---
# AssemblyAI Contract-safe CI

## Overview

Build AssemblyAI CI with offline REST, Streaming v3, webhook, gateway, secret, and lifecycle tests plus a tightly gated live lane. Treat live audio, transcript content, credentials, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The AssemblyAI project, environment, region, data classification, and accountable owner.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

CI covers required model selection, job states, v3 turns and termination, both webhook schemas, gateway output contracts, retry bounds, and redaction. Live checks require protected secrets, synthetic audio, explicit regional routing, and hard request and spend budgets.

## Authentication

For live work, inject `ASSEMBLYAI_API_KEY` from an approved secret manager and send the raw value only in the AssemblyAI `Authorization` header to the configured first-party host. Never print, commit, place in a URL, or expose it to an untrusted client. Callback secrets and temporary streaming tokens are separate credentials.

## Instructions

1. Build synthetic audio and response fixtures for used surfaces.
2. Reject legacy v2 and LeMUR identifiers and missing model lists.
3. Test job success, terminal error, timeout, throttling, and duplicate reconciliation.
4. Test v3 begin, turns, malformed messages, disconnect, and termination.
5. Test callback auth, quick acknowledgment, duplicate delivery, and delayed work.
6. Scan artifacts for keys, URLs, audio, text, prompts, and tokens.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call AssemblyAI, upload audio, open a streaming session, mint a token, replay a callback, deploy, rotate a key, or delete a transcript merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live audio processing, production credential or endpoint changes, paid model or capacity changes, content retention, callback replay, deployment, or deletion. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Mocked happy paths alone miss lifecycle boundaries.
- Live tests on every pull request create uncontrolled cost.
- Full transcript snapshots leak content into CI artifacts.

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
