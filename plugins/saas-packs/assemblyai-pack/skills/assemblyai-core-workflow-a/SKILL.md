---
name: assemblyai-core-workflow-a
description: >-
  Analyze and operate a production AssemblyAI pre-recorded pipeline with explicit models, Speech Understanding, callbacks, and retention controls. Use when running asynchronous transcription. Trigger with "AssemblyAI async transcription" or "pre-recorded pipeline".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<audio-source> <model-policy> <output-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, assemblyai]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live AssemblyAI work requires network access"
---
# AssemblyAI Governed Pre-recorded Pipeline

## Overview

Operate pre-recorded transcription as an auditable asynchronous job. Keep live audio, credentials, spend, retention, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The AssemblyAI project, environment, region, data classification, and accountable owner.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Submit to `/v2/transcript` with explicit `speech_models`; complete by bounded polling or authenticated webhook, then retrieve by transcript ID. Verify every intelligence, redaction, language, and prompting parameter against the selected current model. Route new LLM analysis to LLM Gateway, not deprecated transcript summary parameters.

## Authentication

For live work, inject `ASSEMBLYAI_API_KEY` from an approved secret manager and send the raw value only in the AssemblyAI `Authorization` header to the configured first-party host. Never print, commit, place in a URL, or expose it to an untrusted client. Callback secrets and temporary streaming tokens are separate credentials.

## Instructions

1. Confirm consent, purpose, region, language, and model policy.
2. Request only supported, approved transcription and understanding features.
3. Deliver audio without exposing storage credentials.
4. Persist transcript ID and an internal dedupe key after one submission.
5. Validate terminal status, duration, model, and redaction before release.
6. Propagate retention and deletion to every downstream copy.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call AssemblyAI, upload audio, open a streaming session, mint a token, replay a callback, deploy, rotate a key, or delete a transcript merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live audio processing, production credential or endpoint changes, paid model or capacity changes, content retention, callback replay, deployment, or deletion. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Unsupported features require redesign, not silent omission.
- Reconcile the ledger before resubmission to avoid duplicate cost.
- Speaker labels remain pseudonymous unless identity mapping is separately approved.

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
