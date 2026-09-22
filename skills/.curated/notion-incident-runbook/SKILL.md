---
name: notion-incident-runbook
description: >-
  Analyze and coordinate a Notion integration incident with bounded mitigation, evidence custody, communications, and recovery verification. Use when availability, correctness, privacy, or credential safety is at risk. Trigger with "run Notion incident", "triage Notion outage", or "contain Notion sync failure".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<severity> <environment> <incident-window>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, incident]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Integration Incident Command

## Overview

Analyze and coordinate a Notion integration incident with bounded mitigation, evidence custody, communications, and recovery verification.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Separate Notion service health, authentication, access, version shape, application defects, queues, downstream systems, and data correctness. Availability recovery does not prove data reconciliation. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

If compromise is suspected, freeze token use and follow the approved secret-rotation lane; never expose credentials in the incident channel.

## Instructions

1. Name the incident commander, severity, affected tenants, operations, data classes, and start time.
2. Freeze unsafe writes and retries while preserving queue, cursor, request-ID, and deployment evidence.
3. Classify the fault domain and compare official status with application telemetry.
4. Choose the smallest reversible mitigation with an owner and rollback trigger.
5. Restore service in stages, then reconcile pages, cursors, webhook signals, duplicates, and missed work.
6. Close only after security, data correctness, communications, and follow-up ownership are evidenced.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

The incident commander approves mitigation; security approves token actions; content and data owners approve replay, backfill, or destructive correction.

## Error Handling

- Do not replay a write queue before idempotency is proven.
- Do not blame the vendor solely from correlated timing.
- Escalate immediately on suspected cross-tenant or credential exposure.

## Output

Return the timeline, scope, evidence, hypotheses, decisions, mitigation, reconciliation ledger, communications, and follow-ups. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Contain a retry storm while preserving unacknowledged jobs.
- Recover after service restoration and prove no pages were duplicated.

## Validation

Exercise and record these paths with expected and observed results:

- write freeze
- credential compromise
- service recovery
- queue replay
- data reconciliation
- communications

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
