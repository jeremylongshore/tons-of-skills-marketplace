---
name: ideogram-cost-tuning
description: >-
  Govern Ideogram prepaid spend through admission budgets, route choice, output bounds, useful-result accounting, and cleanup. Use when reducing cost or designing billing controls. Trigger with "cut Ideogram spend", "budget Ideogram generations", or "audit Ideogram API cost".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workload> <budget-window> <quality-floor>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, cost]
model: inherit
effort: high
compatibility: "Designed for Claude Code; current prices must be checked at decision time"
---
# Ideogram Cost Governance

## Overview

Control prepaid Ideogram consumption without embedding prices that can drift. Tie admission to an accountable budget, choose the narrowest route, bound outputs and retries, and measure durable safe results rather than HTTP success or generated candidates.

## Prerequisites

- Team billing owner, current balance source, budget period, workload owner, and quality floor.
- Request volume, endpoint and rendering mix, output count, retry rate, unsafe rate, and storage failures.
- A current pricing review from the first-party API pricing page.

## Current Contract

Ideogram API billing is separate from the web application, requires positive prepaid credit, and can use auto-recharge. Keys in one team share credits and billing, so per-key usage is not a separate vendor balance. Prices and recharge choices are time-sensitive and must be verified rather than copied into this skill.

## Authentication

Workers use server-side `IDEOGRAM_API_KEY` as `Api-Key` to `https://api.ideogram.ai`. Cost evidence may include team, endpoint, request, and opaque generation identifiers, but not the key, prompts, images, or URLs.

## Instructions

1. Retrieve current first-party pricing and balance behavior, recording date, currency, unit, and owner.
2. Inventory demand by tenant, use case, route, rendering option, output count, retry class, safety result, and durable-storage result.
3. Define request, tenant, daily, campaign, and incident ceilings with fail-closed admission.
4. Choose the least costly route that still meets model, quality, transparency, edit, or tool requirements.
5. Prevent duplicate paid work by persisting async identifiers, bounding retries, expiring stale queue items, and deduplicating callers.
6. Attribute spend to useful safe assets that reached durable storage; surface unsafe, failed, abandoned, and expired-URL waste separately.
7. Canary each tuning change and retain a quality, safety, latency, and rollback comparison.

## Tool Discipline

Use Read, Glob, and Grep for billing adapters, queues, metrics, and fixtures. Use Write and Edit for approved budgets, tests, or documentation. Do not add credit, enable auto-recharge, change prices, or run paid experiments by invocation alone.

## Approval Boundaries

Require owners for balance additions, recharge settings, budget changes, lower-quality routes, deleted queued work, paid benchmarks, and production rollout. Cost reduction cannot override safety, rights, or retention policy.

## Error Handling

- Stop admission before balance exhaustion; repeated failures are not a budget strategy.
- Do not retry validation, auth, unsafe, or already accepted async work automatically.
- An image that was never durably stored is waste even if generation succeeded.

## Output

Return pricing review date, budget model, demand and waste breakdown, selected controls, expected and measured impact, quality and safety guardrails, owner, canary, and rollback. Avoid hard-coded future price claims.

## Examples

- Cap a campaign by useful stored assets and expire queued requests when the publication deadline passes.
- Report `submitted=100; safe=92; stored=90; duplicates=0; expired_before_submit=14; budget=within-limit`.

## Validation

Reconcile application counts with vendor billing evidence, inject budget exhaustion, retry ambiguity, unsafe output, and storage failure, then verify admission closes. Recheck pricing immediately before approving a financial decision.

## Resources

- [Current first-party evidence map](references/official-docs.md) — use the dated endpoint, webhook, billing, team, and training links as the contract index for this workflow.
- Recheck the endpoint-specific page and current OpenAPI description before relying on an enum, limit, beta feature, or lifecycle claim.
- Record live observations as environment-specific evidence, not as universal vendor guarantees.
