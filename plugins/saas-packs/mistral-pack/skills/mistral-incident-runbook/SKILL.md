---
name: mistral-incident-runbook
description: >-
  Analyze, contain, and recover Mistral credential, outage, throttling, data, spend, and state-reconciliation incidents. Use when responding to provider-related impact. Trigger with "Mistral incident", "Mistral outage", or "rotate a leaked Mistral key".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<incident-id> <severity> <environment>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, incident-response]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral Incident Response

## Overview

Restore safety before throughput. Classify, stop amplification, protect evidence, reconcile ambiguous work, and use the smallest reversible containment action.

## Prerequisites

- An incident commander, severity policy, inventory, and current runbooks.
- Content-free telemetry, deployment controls, rotation, and admin/status evidence.
- Communication, evidence-retention, and post-incident owners.

## Current Contract

Provider, account, app, and data incidents differ. Workspace caps can suspend access; Files, Batch, Conversations, Agents, and Workflows may outlive a failed request and need reconciliation.

## Authentication

Never paste keys into incident channels. On exposure, revoke through approved admin, rotate consumers, and verify old-key denial without displaying values.

## Instructions

1. Declare scope, severity, commander, UTC timeline, environments, and impact.
2. Stop retry storms and risky work while preserving queue/idempotency evidence.
3. Classify credential, provider, capacity, spend, data, model, deploy, or state failure.
4. Choose bounded containment: disable, shed, pause, rollback, rotate, or isolate.
5. Reconcile files, jobs, runs, conversations, and app actions before replay.
6. Recover through synthetic canary, monitor convergence, communicate, and assign actions.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

The commander must approve revocation, traffic, queue or job changes, deletion, limits or spend changes, rollback, and customer communication. Record the approver and exact containment scope.

## Error Handling

- Blind replay can duplicate paid/stateful work.
- Purging queues can destroy reconciliation evidence.
- Provider recovery does not prove app backlog convergence.

## Output

Return scope and timeline, classification, containment approvals, affected state, reconciliation, recovery, residual risk, communications, and follow-ups. Keep unresolved ambiguity visible with a named owner.

## Examples

- Disable batch submission while reconciling accepted jobs.
- Rotate an exposed key and prove old-key denial plus new-key canary.

## Validation

Tabletop key exposure, `429`, outage, cap reached, content leak, stuck stream, and ambiguous state; verify rollback/comms.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
