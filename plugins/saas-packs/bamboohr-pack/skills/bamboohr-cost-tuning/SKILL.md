---
name: bamboohr-cost-tuning
description: >-
  Reduce the operational cost of a BambooHR connector by removing redundant
  traffic, oversized data retention, retry waste, and support toil without
  claiming undocumented API prices. Use when budgeting or right-sizing an HR
  integration. Trigger with "BambooHR cost", "BambooHR request waste", or
  "BambooHR integration budget".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<pipeline-path> <measurement-window>"
version: 1.5.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, hr, bamboohr, cost, operations]
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# BambooHR Operational Cost Tuning

## Overview

Optimize costs the team can actually measure: compute, egress, storage,
observability, queue backlog, failure recovery, and engineering/support time.
Do not quote a per-call BambooHR price or numeric quota unless the customer's
current contract or a current official price source explicitly provides it.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The tenant, identity, and data scope only when approved live work is in scope.
- The current evidence register plus customer-specific permissions and agreements.

## Current Contract

BambooHR's dataset v2 projection and pagination can reduce request fan-out and
unnecessary fields. The official SDK exposes bounded retries and redacted
logging. These capabilities reduce waste only when the integration measures
requests, bytes, attempts, and retained data.

## Authentication

Separate usage by tenant and credential alias without embedding keys or tokens
in cost logs. Auth failures are operational waste and potential security events;
do not solve them by using one broader shared credential.

## Instructions

1. Choose a representative window and measure request count by operation,
   transferred bytes, retries, failed jobs, queue time, compute duration,
   storage/backup growth, log volume, and human incident time.
2. Assign each call to a business output. Mark duplicates, polling with no state
   change, N+1 employee calls, deprecated report traffic, and repeated failures.
3. Replace fan-out with minimized dataset v2 projections where semantics match.
   Use deterministic pagination and retain only approved fields.
4. Cache stable metadata with an owner and TTL. Prefer checkpoints and change-
   aware workflows to blind full refreshes, but keep periodic reconciliation.
5. Cap retries and dead-letter terminal work. A retry storm converts an outage
   into cost and rate pressure without producing value.
6. Reduce log payloads to safe operational fields and set retention by purpose.
   HR response bodies should not be an observability cost center.
7. Model candidate savings from measured infrastructure unit rates and labor
   assumptions. Label BambooHR contract costs as customer-supplied, not inferred.
8. Canary the change and compare cost, freshness, completeness, error rate, and
   recovery time before rollout.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, and existing metrics.
Use Write/Edit only for approved measurement, optimization, and tests. Do not
access invoices, production HR data, or billing systems under this skill.

## Approval Boundaries

Require approval before changing refresh frequency, fields, retention, cache,
concurrency, reconciliation cadence, or a customer-contract assumption. Cost
reduction may not weaken privacy, completeness, or recovery objectives.

## Output

Return measured baseline, waste categories, candidate changes, explicit price
sources/assumptions, projected range, risk to freshness/completeness, canary
result, rollback thresholds, and realized savings after observation.

## Error Handling

- No trustworthy baseline: implement measurement before claiming savings.
- Contract pricing unavailable: report operational costs only.
- Savings regress data quality or security: reject or redesign the change.

## Examples

- "What does the BambooHR API cost?" separates customer contract facts from connector costs.
- "Cut sync spend" identifies N+1 calls, retry waste, and excessive retention first.

## Resources

Read [official evidence](references/official-docs.md) before choosing optimizations.
