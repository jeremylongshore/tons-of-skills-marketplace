---
name: assemblyai-performance-tuning
description: >-
  Analyze and tune AssemblyAI model choice, audio delivery, polling, Streaming v3 turns, concurrency, and downstream work. Use when pursuing measured latency or throughput goals. Trigger with "tune AssemblyAI" or "AssemblyAI latency".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workload-profile> <service-level-objective>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, assemblyai]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live AssemblyAI work requires network access"
---
# AssemblyAI Latency and Throughput Tuning

## Overview

Tune latency and throughput with controlled, representative experiments. Preserve accuracy, privacy, credentials, spend, and rollback as separate gates.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The AssemblyAI project, environment, region, data classification, and accountable owner.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Pre-recorded and streaming optimize different outcomes. Current models differ in languages, accuracy, latency, prompting, endpointing, and price. Benchmark representative approved fixtures rather than inherited labels such as Best or Nano, and keep privacy, quality, and spend as co-equal gates.

## Authentication

For live work, inject `ASSEMBLYAI_API_KEY` from an approved secret manager and send the raw value only in the AssemblyAI `Authorization` header to the configured first-party host. Never print, commit, place in a URL, or expose it to an untrusted client. Callback secrets and temporary streaming tokens are separate credentials.

## Instructions

1. Define queue, completion, first-turn, finalization, quality, and cost objectives.
2. Build a representative synthetic or approved evaluation set.
3. Benchmark current supported models and only required features.
4. Replace aggressive polling with callbacks and tune admission separately.
5. Verify audio format, pacing, turn settings, and termination for streaming.
6. Canary one change at a time and retain rollback thresholds.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call AssemblyAI, upload audio, open a streaming session, mint a token, replay a callback, deploy, rotate a key, or delete a transcript merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live audio processing, production credential or endpoint changes, paid model or capacity changes, content retention, callback replay, deployment, or deletion. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Faster output with unacceptable accuracy is a regression.
- Audio preprocessing can introduce harmful artifacts.
- Lower latency with more retries or abandoned sessions is not an improvement.

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
