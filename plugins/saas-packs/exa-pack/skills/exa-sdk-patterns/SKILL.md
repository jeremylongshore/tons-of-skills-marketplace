---
name: exa-sdk-patterns
description: >-
  Isolate exa-js or exa-py behind an application-owned adapter that preserves current request semantics and safe evidence. Use when operating or reviewing this Exa boundary. Trigger with "Exa sdk patterns", "review Exa sdk patterns", or "fix Exa sdk patterns".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<typescript-or-python> <adapter-path>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa SDK Adapter Patterns

## Overview

Isolate exa-js or exa-py behind an application-owned adapter that preserves current request semantics and safe evidence. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

The JavaScript and Python SDKs expose Search, Contents, Answer, Agent, and Monitor surfaces with language-specific naming. The adapter should normalize application inputs and errors without inventing defaults, and it should preserve requestId, statuses, grounding, and costDollars needed for operations.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Pin the selected SDK and inspect its current first-party specification.
2. Define the smallest application-owned interface for the required product surface.
3. Map names and optional fields explicitly at the adapter boundary.
4. Return content-free operational metadata separately from retrieved content.
5. Normalize documented errors without erasing status, tag, or request ID.
6. Add fixture-backed contract tests before changing the pinned SDK.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Do not expose the vendor client throughout business logic.
- Do not assume Python snake_case and TypeScript camelCase are interchangeable.
- Do not silently fall back between Search, Answer, Agent, or Contents products.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- A search adapter accepts an owned SearchRequest and returns owned results plus request ID and cost, keeping SDK types at one module boundary.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
