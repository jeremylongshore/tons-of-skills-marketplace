---
name: adobe-architecture-variants
description: >-
  Choose among direct service integration, Adobe App Builder, and a dedicated queued worker using evidence about ownership, latency, scale, storage, events, and operations. Use when the task requires adobe architecture variant decision. Trigger with "choose Adobe architecture", "App Builder or microservice", or "Adobe design options".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workloads> <constraints> <decision-date>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, architecture-decision]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Architecture Variant Decision

## Overview

Choose among direct service integration, Adobe App Builder, and a dedicated queued worker using evidence about ownership, latency, scale, storage, events, and operations. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

Direct integration minimizes platform layers, App Builder offers Adobe-native Runtime/workspaces/events, and dedicated workers maximize queue/storage portability. None removes the need for auth, entitlement, async lifecycle, data custody, observability, and rollback. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Score how each variant binds S2S/user credentials, organization/project/workspace, product profiles, secret storage, and deployment authority.

## Instructions

1. Capture workload operations, data owners, latency/throughput, budgets, team skills, compliance, RTO/RPO, and portability needs.
2. Model direct server-side adapters, App Builder Runtime, and dedicated queued workers against the same service contracts.
3. Compare auth/entitlement, async jobs, storage custody, events, limits, observability, failure isolation, deployment, and lock-in.
4. Prototype the riskiest seam with synthetic data and measure rather than inventing latency or scale claims.
5. Threat-model each variant and name compensating controls, operational owners, exit cost, and rollback.
6. Issue a dated decision with rejected options, evidence, conditions, review triggers, and migration seam.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Architecture, security, data, budget, and operations owners approve the decision. A prototype does not authorize production data, spend, deploy, or destructive actions.

## Error Handling

- Reject browser-side client-secret designs.
- Reject App Builder claims that assume Runtime namespace auth for current deploys.
- Reject direct synchronous handlers for unbounded async work.

## Output

Return decision drivers, comparison matrix, prototype evidence, threats, selected variant, conditions, exit plan, and review date. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Compare a Firefly async worker in all three variants.
- Show how each variant handles credential revocation and unknown jobs.

## Validation

Exercise and record expected and observed results for:

- auth
- async workload
- storage
- event ingress
- vendor outage
- exit

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
