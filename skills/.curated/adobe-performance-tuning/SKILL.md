---
name: adobe-performance-tuning
description: >-
  Improve Adobe integration latency and throughput from measurements while preserving correctness, policy, and spend boundaries. Use when the task requires adobe measured performance tuning. Trigger with "tune Adobe performance", "reduce Firefly latency", or "optimize PDF jobs".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<service-operation> <measurement-window> <objective>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, performance]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Measured Performance Tuning

## Overview

Improve Adobe integration latency and throughput from measurements while preserving correctness, policy, and spend boundaries. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

No universal Adobe latency table is a production contract. Measure token reuse, queue wait, upload/download, submission, status polling, vendor processing, validation, and downstream work separately by service and operation. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Use content-free metrics and aliases. Token reuse must honor actual expiry response and revocation; cached signed URLs and customer outputs are not performance caches by default.

## Instructions

1. Define objective, workload, input class, concurrency, cost ceiling, completeness, and measurement window.
2. Instrument queue, transport, vendor job, polling, storage transfer, validation, retry, and downstream spans.
3. Measure percentiles, 429s, failures, bytes, transactions/generations, and artifact correctness from a synthetic canary.
4. Test token reuse, connection reuse, right-sized inputs, bounded concurrency, adaptive polling, and safe deduplication independently.
5. Canary one change within current documented constraints and compare correctness plus spend, not latency alone.
6. Retain verified gains with rollback thresholds and remove instrumentation that captures sensitive content.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Workload, data, and budget owners approve load or generation tests. Do not increase credentials or identities to manufacture throughput.

## Error Handling

- Delete invented benchmark tables.
- Do not parallelize past queue, spend, or service evidence.
- Roll back if output correctness, content provenance, throttling, or cost worsens.

## Output

Return baseline spans, bottleneck attribution, experiments, before/after percentiles, correctness/spend proof, selected change, and rollback. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Compare fixed polling with bounded response-led adaptive polling.
- Prove token reuse stops on actual expiry or revocation.

## Validation

Exercise and record expected and observed results for:

- queue wait
- upload bottleneck
- 429
- unknown status
- cache staleness
- rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
