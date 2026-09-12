---
name: assemblyai-prod-checklist
description: >-
  Analyze and gate an AssemblyAI integration across contracts, security, reliability, cost, observability, retention, and rollback. Use when preparing a launch or material change. Trigger with "AssemblyAI production checklist" or "go live".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<service> <environment> <release-sha>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, assemblyai]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live AssemblyAI work requires network access"
---
# AssemblyAI Production Readiness Gate

## Overview

Gate production on evidence across the entire AssemblyAI lifecycle. Treat data, credentials, spend, deployment, rollback, and deletion as separately owned boundaries.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The AssemblyAI project, environment, region, data classification, and accountable owner.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Production requires current REST and Streaming v3 contracts, explicit models, protected keys and tokens, authenticated idempotent callbacks, bounded retries, explicit streaming termination, deletion propagation, cost controls, monitoring, and tested rollback. One happy-path transcript is insufficient.

## Authentication

For live work, inject `ASSEMBLYAI_API_KEY` from an approved secret manager and send the raw value only in the AssemblyAI `Authorization` header to the configured first-party host. Never print, commit, place in a URL, or expose it to an untrusted client. Callback secrets and temporary streaming tokens are separate credentials.

## Instructions

1. Record release, owners, regions, data classes, surfaces, and rollback target.
2. Verify secrets, consent, token issuance, callbacks, and retention.
3. Test success, terminal error, 429, duplicate, malformed event, reconnect, and termination offline.
4. Run one budgeted live synthetic canary in the approved region.
5. Verify alerts for queue age, failures, throttling, delivery, sessions, and spend.
6. Exercise rollback and publish an expiring pass or fail receipt.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call AssemblyAI, upload audio, open a streaming session, mint a token, replay a callback, deploy, rotate a key, or delete a transcript merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live audio processing, production credential or endpoint changes, paid model or capacity changes, content retention, callback replay, deployment, or deletion. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- A health endpoint that never submits audio is not integration evidence.
- Customer audio is not a synthetic production test.
- An alert without an owner and response action is not ready.

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
