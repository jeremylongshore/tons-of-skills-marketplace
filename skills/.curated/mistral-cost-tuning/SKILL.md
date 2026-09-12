---
name: mistral-cost-tuning
description: >-
  Control Mistral spend with live account rates, usage attribution, admission budgets, and quality-preserving experiments. Use when forecasting or reducing cost. Trigger with "optimize Mistral cost", "set a Mistral budget", or "explain Mistral spend".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workspace> <workload> <budget-period>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, cost]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral Spend and Usage Governance

## Overview

Turn spend into an attributable operating signal. Use live billing/model evidence, distinguish attempted from completed work, and require quality and safety evaluation before workflow changes.

## Prerequisites

- Authorized billing/usage evidence with observation time.
- Operation-level usage, retry, caching, and business-outcome metrics.
- A spend owner, budget period, alerts, and evaluation set.

## Current Contract

Billing, model rates, and workspace limits vary by plan and time. Do not hard-code a price table, context size, batch discount, or model recommendation.

## Authentication

Billing review uses an authorized admin session; inference uses the server-side key. Receipts exclude credentials, prompts, responses, invoices, and personal billing details.

## Instructions

1. Capture current rates, feature charges, usage, caps, and evidence times from authorized views.
2. Attribute requests, tokens, retries, files, batch, OCR, audio, and stateful work to operations.
3. Calculate unit cost and waste from retries, abandonment, excessive context, and duplicates.
4. Prioritize admission budgets, request bounds, deduplication, and scheduling.
5. Evaluate model, batch, or routing changes against the same correctness and safety set.
6. Alert on cap approach, cap reached, invoice failure, and unattributed use with fail-safe behavior.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Spend-cap changes, purchases, model/endpoint substitution, batch conversion, and production routing require approval. Never raise a cap automatically.

## Error Handling

- Lower unit price can raise total spend through output, retry, or failure changes.
- Batch economics and eligibility must be rechecked.
- Unattributed usage is an incident signal.

## Output

Return dated rates and limits, attribution, unit economics, waste, evaluated options, controls, owner, and rollback. Separate observed facts from forecasts and assumptions.

## Examples

- Reduce duplicate retries before evaluating a cheaper model.
- Alert on forecast budget crossing while preserving admission bounds.

## Validation

Reconcile provider totals to app attribution, sample retry accounting, test cap-reached behavior, and preserve quality/safety/tenancy.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
