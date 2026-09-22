---
name: mistral-prod-checklist
description: >-
  Issue a fail-closed Mistral go-live decision from auth, reliability, spend, data, security, and rollback evidence. Use when reviewing a production launch. Trigger with "Mistral production checklist", "approve Mistral go-live", or "review Mistral launch readiness".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<service> <environment> <release-sha>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, production]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral Production Readiness Gate

## Overview

Turn readiness into an evidence-backed decision. Missing ownership, unsafe data, unbounded demand, or untested rollback blocks launch.

## Prerequisites

- An immutable candidate and environment inventory.
- Named service, security, privacy, spend, and incident owners.
- Current model/API evidence, load results, data policy, runbook, and rollback proof.

## Current Contract

Model access, limits, billing, and preview status can change. Evidence must be timestamped and environment-specific; Public Preview surfaces need an explicit risk decision.

## Authentication

Verify secret injection, isolation, rotation ownership, and absence from artifacts without displaying credential values. Confirm the production runtime cannot expose the secret to browser code.

## Instructions

1. Pin release, dependency lock, endpoints, model policy, and provider evidence.
2. Review auth, tenancy, safety, file/data lifecycle, and ZDR applicability.
3. Review deadlines, retries, backpressure, state reconciliation, and degradation.
4. Prove usage attribution, spend caps, alerts, and billing ownership.
5. Run offline gates and approved canary tests including failure and rollback.
6. Record PASS, CONDITIONAL, or BLOCKED with owner and evidence per gap.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

This skill cannot deploy, enable preview APIs, increase limits, upload data, mutate keys, or waive a failed gate.

## Error Handling

- A successful health call does not prove load safety or rollback.
- Undocumented fallback can silently alter cost and behavior.
- Rollback leaving queues/files/state unreconciled is incomplete.

## Output

Return release/environment, gate matrix, evidence times, blockers, accepted preview risks, decision, approvers, canary, and rollback receipt.

## Examples

- Block launch when spend alerts and tenant tests lack evidence.
- Approve only a fixed-bound canary with a verified disable switch.

## Validation

Re-run every gate at the exact SHA, exercise rollback/provider failure, and verify evidence links and owners.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
