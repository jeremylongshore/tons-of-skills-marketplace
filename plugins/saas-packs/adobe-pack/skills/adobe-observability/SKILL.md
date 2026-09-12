---
name: adobe-observability
description: >-
  Instrument Adobe integrations with redacted structured logs, request/job/activation correlation, service-level indicators, alerts, and evidence retention. Use when the task requires adobe content-safe observability. Trigger with "monitor Adobe API", "Adobe observability", or "App Builder logs".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<services> <objectives> <telemetry-destination>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, observability]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Content-Safe Observability

## Overview

Instrument Adobe integrations with redacted structured logs, request/job/activation correlation, service-level indicators, alerts, and evidence retention. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

App Builder local, Runtime activation, CLI, and Console log surfaces differ. Successful activation persistence is mode-dependent; current Console application logs can provide broader visibility. Runtime log size and retention are bounded and mutable. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Log service, operation, environment aliases, request/job/activation IDs, state, status class, duration, retry, bytes, and usage class. Never log secrets, Authorization, signed URLs, prompts, document/image/event content, or direct identifiers.

## Instructions

1. Define SLOs, telemetry consumers, data classification, retention, and incident evidence needs.
2. Inventory logs, metrics, traces, dashboards, activations, queue evidence, and current blind spots by execution mode.
3. Create a redacted correlation model from ingress through queue, Adobe request/job, storage, and downstream acknowledgement.
4. Measure availability, terminal success, queue age, vendor time, 429s, retries, unknown jobs, duplicates, and cleanup lag.
5. Add alerts tied to actionable runbooks, budget limits, credential/EOL dates, event disablement, and stale assets.
6. Run content/secret/URL canaries, failure drills, retention verification, and dashboard reconciliation.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Security and data owners approve telemetry fields and destinations; operations owns alerts and retention. Extra logging or external forwarding requires explicit approval.

## Error Handling

- Do not enable production extra logging as a default workaround.
- Do not treat missing successful activations as zero traffic.
- Stop telemetry export if content or signed-URL canaries appear.

## Output

Return telemetry schema, redaction rules, SLO/SLI definitions, dashboards, alert/runbook mapping, canary evidence, gaps, and owners. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Correlate one async job without logging its prompt or output URL.
- Trigger and resolve a synthetic disabled-event or 429 alert.

## Validation

Exercise and record expected and observed results for:

- success
- 429
- unknown job
- vendor outage
- content canary
- retention expiry

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
