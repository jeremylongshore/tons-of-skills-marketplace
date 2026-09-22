---
name: onenote-performance-tuning
description: >-
  Improve OneNote read and write latency from measured evidence while preserving completeness and service limits. Use when an integration misses a latency or throughput objective. Trigger with "tune OneNote performance", "reduce OneNote calls", or "optimize OneNote paging".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<operation> <measurement-window> <objective>"
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, onenote, performance]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live OneNote actions require network access, delegated authentication, and explicit approval"
---
# OneNote Measured Performance Tuning

## Overview

Improve OneNote read and write latency from measured evidence while preserving completeness and service limits.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Microsoft Graph OneNote documentation and the selected integration's tested contract.
- Named identity, content, workload, security, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures with secrets and real notebook content removed.

## Current Contract

Microsoft recommends selecting only required properties, expanding safe hierarchy relationships, enumerating pages per section, and overriding the default last-modified ordering when that sort is unnecessary. Every response page still requires completeness accounting. Recheck the dated evidence map before relying on mutable permissions, limits, SDK behavior, supported resources, or cloud availability.

## Authentication

Measure under delegated user and location aliases without content labels. Use synthetic or approved non-sensitive workloads.

## Instructions

1. Define the operation, service-level objective, location, volume, and completeness requirement.
2. Measure latency, calls, response pages, bytes, concurrency, 429s, retries, and downstream time.
3. Attribute cost to hierarchy fan-out, all-pages scans, unnecessary fields, default sorting, content fetches, and writes.
4. Test selected fields, safe expansion, section-scoped enumeration, caching, and bounded batching independently.
5. Canary one change within documented concurrency and request budgets.
6. Compare percentile latency and completeness, then retain only verified gains with rollback thresholds.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, delegated credentials, tenant or notebook content, consent, file transfer, deployment, writes, spend, sharing changes, or deletion.

## Approval Boundaries

Require the workload and data owner before tests. Never load-test production notebooks or increase identity count to evade limits.

## Error Handling

- Do not optimize away next-link traversal.
- Do not assume batching bypasses per-request throttling.
- Roll back on missing pages, stale state, or increased throttling.

## Output

Return the baseline, bottleneck evidence, candidate experiments, before and after metrics, completeness proof, selected change, and rollback. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Compare all-pages retrieval with section-scoped enumeration.
- Measure selected fields and expansion without exposing page bodies.

## Validation

Exercise and record these paths with expected and observed results:

- multi-page response
- many sections
- 429
- cache staleness
- batch partial failure
- rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal OneNote guarantee.
