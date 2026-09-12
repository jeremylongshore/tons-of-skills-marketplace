---
name: exa-upgrade-migration
description: >-
  Upgrade Exa SDK or API usage through a contract inventory, fixture diff, canary, and reversible dependency change. Use when operating or reviewing this Exa boundary. Trigger with "Exa upgrade migration", "review Exa upgrade migration", or "fix Exa upgrade migration".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<current-version> <target-version> <adapter-path>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa SDK and API Upgrade Migration

## Overview

Upgrade Exa SDK or API usage through a contract inventory, fixture diff, canary, and reversible dependency change. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Current Search uses auto, fast, instant, deep-lite, deep, and deep-reasoning; neural is legacy terminology for new code. SDK method names and request casing differ by language, and newer product surfaces may be beta-gated. The first-party SDK specifications and changelog are the migration authority.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Record current dependency, lockfile, endpoint calls, types, headers, and feature flags.
2. Read the target SDK specification and Exa changelog for breaking changes.
3. Diff owned fixtures for requests, responses, errors, statuses, and costs.
4. Update only the application adapter and regenerate its lockfile deterministically.
5. Run offline contracts, then an approved synthetic canary on the target version.
6. Retain a dependency rollback and remove compatibility code only after observation.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Do not automatically fall back to an older SDK or search type.
- A compile pass does not prove response, error, or billing compatibility.
- Beta headers and features must remain explicit and independently removable.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Replace a legacy neural request with auto only after fixture and relevance acceptance tests confirm the intended behavior.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
