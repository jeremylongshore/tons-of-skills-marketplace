---
name: exa-performance-tuning
description: >-
  Tune Exa search type, content mode, freshness, result count, and concurrency against measured latency and retrieval quality. Use when operating or reviewing this Exa boundary. Trigger with "Exa performance tuning", "review Exa performance tuning", or "fix Exa performance tuning".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workload> <latency-slo> <quality-metric>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Latency and Retrieval Performance Tuning

## Overview

Tune Exa search type, content mode, freshness, result count, and concurrency against measured latency and retrieval quality. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Search types trade latency and synthesis depth; content extraction, outputSchema, forced livecrawl, summaries, and subpages add work. Highlights are usually more token-efficient than full text. Published latency values are guidance, not a service-specific SLO.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Build a consented benchmark set with explicit relevance and freshness judgments.
2. Measure the current adapter end to end, including queue and downstream processing.
3. Vary one dimension at a time: type, result count, content mode, freshness, or subpages.
4. Track p50, p95, errors, content size, relevance, freshness, and cost together.
5. Choose separate profiles for interactive, background, and deep-research paths.
6. Canary the winning profile and retain rollback thresholds.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Faster results can be less relevant or stale.
- Forced livecrawl and deep synthesis stack latency rather than replacing it.
- Vendor request latency alone omits queues, parsing, reranking, and model consumption.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Compare fast plus highlights against auto plus capped text on the same query set and promote only if the quality floor holds.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
