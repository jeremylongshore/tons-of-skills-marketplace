---
name: notion-observability
description: >-
  Design content-safe metrics, logs, traces, alerts, and reconciliation signals for a Notion integration. Use when making operations diagnosable without leaking workspace data. Trigger with "instrument Notion integration", "monitor Notion sync", or "design Notion alerts".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workload> <service-objectives> <data-classification>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, observability]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Integration Observability Contract

## Overview

Design content-safe metrics, logs, traces, alerts, and reconciliation signals for a Notion integration.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Operational signals should distinguish operation class, status, structured code, request ID, latency, retry, queue age, cursor age, and reconciliation delta. Page IDs, titles, content, user data, tokens, and signed URLs are unsafe default labels. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Telemetry pipelines receive no bearer or verification tokens. Use tenant aliases and bounded fingerprints approved for the monitoring boundary.

## Instructions

1. Define service, freshness, correctness, and security objectives with owners.
2. Create a low-cardinality operation taxonomy covering reads, writes, webhooks, queues, files, and reconciliation.
3. Specify redaction before serialization and sampling after security events are preserved.
4. Correlate attempts with internal operation IDs and vendor request IDs without content.
5. Alert on sustained error class, Retry-After pressure, queue age, cursor staleness, and reconciliation drift.
6. Exercise dashboards and alerts with synthetic failures and document response ownership.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require data and security approval before adding identifiers, payload excerpts, user fields, or third-party telemetry processors.

## Error Handling

- Do not use page or workspace IDs as unbounded metric labels.
- A green request-rate dashboard does not prove sync completeness.
- Fail closed if redaction is unavailable.

## Output

Return the signal catalog, redaction contract, objective definitions, dashboards, alerts, runbook links, and test receipts. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Alert on cursor age even when requests return 200.
- Trace a retry chain with request IDs but no page content.

## Validation

Exercise and record these paths with expected and observed results:

- secret canary
- content canary
- cardinality
- alert firing
- reconciliation drift
- telemetry outage

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
