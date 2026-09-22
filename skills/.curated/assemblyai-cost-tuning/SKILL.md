---
name: assemblyai-cost-tuning
description: >-
  Analyze and control AssemblyAI model, feature, duration, retry, concurrency, and LLM Gateway spend using measured usage. Use when setting budgets or investigating anomalies. Trigger with "AssemblyAI cost", "AssemblyAI billing", or "reduce AssemblyAI spend".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workload-profile> <budget>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, assemblyai]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live AssemblyAI work requires network access"
---
# AssemblyAI Spend and Usage Control

## Overview

Control spend with dated prices and measured workload usage. Keep quality, privacy, reliability, credentials, and destructive state as separate gates.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The AssemblyAI project, environment, region, data classification, and accountable owner.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Pre-recorded billing follows successfully processed audio duration and selected models or add-ons; published guidance says failed transcripts are not charged. Streaming follows session duration, so termination matters. LLM Gateway has separate economics. Prices are time-sensitive and belong in reviewed billing inputs.

## Authentication

For live work, inject `ASSEMBLYAI_API_KEY` from an approved secret manager and send the raw value only in the AssemblyAI `Authorization` header to the configured first-party host. Never print, commit, place in a URL, or expose it to an untrusted client. Callback secrets and temporary streaming tokens are separate credentials.

## Instructions

1. Inventory audio and session duration, model mix, features, gateway use, retries, and duplicates.
2. Retrieve dated current prices and account reporting.
3. Attribute usage through internal job metadata rather than keys per customer.
4. Remove duplicate submissions, abandoned sessions, and needless polling.
5. Compare supported models against fixed quality and latency gates.
6. Set budgets, anomaly alerts, and hard ceilings for backfills and gateway work.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call AssemblyAI, upload audio, open a streaming session, mint a token, replay a callback, deploy, rotate a key, or delete a transcript merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live audio processing, production credential or endpoint changes, paid model or capacity changes, content retention, callback replay, deployment, or deletion. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Stale price constants produce false forecasts.
- Separate keys do not create separate account capacity.
- Deletion reduces retention exposure but does not reverse processing cost.

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
