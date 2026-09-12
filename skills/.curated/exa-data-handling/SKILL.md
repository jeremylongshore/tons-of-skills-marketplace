---
name: exa-data-handling
description: >-
  Govern queries, public-web retrieval, generated summaries, citations, and downstream copies across their full retention lifecycle. Use when operating or reviewing this Exa boundary. Trigger with "Exa data handling", "review Exa data handling", or "fix Exa data handling".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<data-class> <content-mode> <retention-window>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Retrieved-content Governance

## Overview

Govern queries, public-web retrieval, generated summaries, citations, and downstream copies across their full retention lifecycle. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Search and Contents can return page text, highlights, summaries, links, images, and subpages; Agent and Answer can generate cited output. Public availability does not remove privacy, copyright, contractual, prompt-injection, or retention obligations. Enterprise Zero Data Retention and request-scoped HIPAA behavior require explicit enablement.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Classify query intent, target domains, returned content, generated output, and citations.
2. Request the smallest content mode and character budget that supports the task.
3. Apply domain, moderation, malware, prompt-injection, and personal-data controls.
4. Keep source attribution and generated claims distinguishable downstream.
5. Define cache, vector-store, log, backup, and deletion propagation before persistence.
6. Verify downstream deletion and preserve only content-free operational receipts.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Highlights are source excerpts; summaries are generated and need different labeling.
- Vector databases and model traces can outlive the application cache.
- Zero Data Retention at the vendor does not delete customer-controlled downstream copies.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Store approved highlights with source URL and expiry, exclude raw full text from logs, and propagate deletion to embeddings and backups.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
