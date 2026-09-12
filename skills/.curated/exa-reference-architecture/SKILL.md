---
name: exa-reference-architecture
description: >-
  Design an Exa architecture that separates query policy, retrieval, content handling, asynchronous state, citations, and evidence. Use when operating or reviewing this Exa boundary. Trigger with "Exa reference architecture", "review Exa reference architecture", or "fix Exa reference architecture".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<use-case> <latency-class> <data-class>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Retrieval Architecture Boundary

## Overview

Design an Exa architecture that separates query policy, retrieval, content handling, asynchronous state, citations, and evidence. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Use Search for ranked discovery, Contents for known URLs, Answer for a direct cited response, Agent for multi-step research, Monitors for recurring discovery, Websets for verified and enriched sets, and Batch for enabled enterprise offline volume. Each product has distinct lifecycle and trust boundaries.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Classify the user outcome, latency class, data sensitivity, freshness, and volume.
2. Select the narrowest Exa product that satisfies the outcome.
3. Place policy and credential enforcement before the vendor adapter.
4. Separate retrieved content from content-free operational metadata and citations.
5. Persist only necessary asynchronous IDs and define terminal-state reconciliation.
6. Diagram failure, retention, deletion, webhook, cost, and rollback boundaries.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Do not use Agent when a bounded Search or Contents call is sufficient.
- Do not feed untrusted retrieved text directly into privileged tool execution.
- Do not share one queue and retry policy across interactive and offline products.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- A RAG service uses Search highlights first, Contents only for selected URLs, a citation-preserving model boundary, and a separate audit stream.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
