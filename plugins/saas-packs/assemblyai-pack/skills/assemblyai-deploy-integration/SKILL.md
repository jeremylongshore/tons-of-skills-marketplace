---
name: assemblyai-deploy-integration
description: >-
  Deploy AssemblyAI workers, Streaming v3 token services, and authenticated callback receivers with reversible controls. Use when shipping cloud infrastructure. Trigger with "deploy AssemblyAI" or "AssemblyAI webhook deployment".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<platform> <environment> <region>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, assemblyai]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live AssemblyAI work requires network access"
---
# AssemblyAI Reversible Deployment

## Overview

Deploy AssemblyAI workers, Streaming v3 token services, and authenticated callback receivers with reversible controls. Treat live audio, transcript content, credentials, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The AssemblyAI project, environment, region, data classification, and accountable owner.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

REST workers need HTTPS egress to the chosen regional host. Streaming needs WebSocket support and shutdown cleanup. Token issuance stays on a trusted backend. Callback ingress uses TLS, authentication, fast durable enqueue, deduplication, and dead-letter handling.

## Authentication

For live work, inject `ASSEMBLYAI_API_KEY` from an approved secret manager and send the raw value only in the AssemblyAI `Authorization` header to the configured first-party host. Never print, commit, place in a URL, or expose it to an untrusted client. Callback secrets and temporary streaming tokens are separate credentials.

## Instructions

1. Draw boundaries for clients, audio, token service, ingress, queue, workers, and stores.
2. Bind immutable region and environment keys from the secret manager.
3. Deploy callback ingress with auth, size limits, durable enqueue, and dedupe.
4. Deploy authorized token issuance with short expiry and quotas.
5. Configure worker concurrency, shutdown, retry, and retention.
6. Canary synthetic REST and v3 paths, then exercise rollback.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call AssemblyAI, upload audio, open a streaming session, mint a token, replay a callback, deploy, rotate a key, or delete a transcript merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live audio processing, production credential or endpoint changes, paid model or capacity changes, content retention, callback replay, deployment, or deletion. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Some serverless platforms cannot hold long WebSockets.
- Acknowledging before durable enqueue can lose work.
- Rollback that leaves token issuance active does not contain traffic.

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
