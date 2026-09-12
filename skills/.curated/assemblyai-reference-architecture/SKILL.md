---
name: assemblyai-reference-architecture
description: >-
  Analyze and design an AssemblyAI architecture spanning pre-recorded jobs, Streaming v3, LLM Gateway, callbacks, queues, retention, and audit evidence. Use when performing system design or review. Trigger with "AssemblyAI architecture" or "design AssemblyAI pipeline".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<use-case> <region> <data-class>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, assemblyai]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live AssemblyAI work requires network access"
---
# AssemblyAI Governed Reference Architecture

## Overview

Design explicit trust and lifecycle boundaries for ingestion, jobs, live turns, analysis, and deletion. Keep data, credentials, region, spend, and destructive state visible.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The AssemblyAI project, environment, region, data classification, and accountable owner.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Pre-recorded jobs are asynchronous resources addressed by transcript ID. Streaming v3 is a stateful billed session requiring termination. LLM Gateway is a separate analysis plane replacing LeMUR. Callback payloads differ by family. Region, principal, credential, retention, and deletion remain visible on every edge.

## Authentication

For live work, inject `ASSEMBLYAI_API_KEY` from an approved secret manager and send the raw value only in the AssemblyAI `Authorization` header to the configured first-party host. Never print, commit, place in a URL, or expose it to an untrusted client. Callback secrets and temporary streaming tokens are separate credentials.

## Instructions

1. Capture use cases, SLOs, languages, data classes, consent, region, retention, and cost.
2. Separate audio ingress, submitter, v3 gateway, token issuer, callback ingress, queues, workers, and stores.
3. Assign each edge a principal, credential, host, timeout, retry budget, and schema.
4. Model job and session states including duplicates, reconnect, failure, and termination.
5. Place LLM Gateway behind prompt allowlists and output schemas.
6. Map deletion through vendor, storage, databases, caches, search, and analytics.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call AssemblyAI, upload audio, open a streaming session, mint a token, replay a callback, deploy, rotate a key, or delete a transcript merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live audio processing, production credential or endpoint changes, paid model or capacity changes, content retention, callback replay, deployment, or deletion. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- One opaque method cannot safely hide REST jobs and streaming sessions.
- Polling in request handlers couples scaling and timeouts.
- A design without credential, failure, rollback, and deletion paths is incomplete.

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
