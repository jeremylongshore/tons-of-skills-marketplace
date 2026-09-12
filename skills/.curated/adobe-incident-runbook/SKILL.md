---
name: adobe-incident-runbook
description: >-
  Triage, contain, recover, and review Adobe auth, product, async-job, event, storage, spend, or App Builder incidents with evidence. Use when this Adobe operator workflow is needed. Trigger with "Adobe incident", "Firefly outage", or "Adobe credential leak".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<service> <impact> <incident-window>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, incident-response]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Integration Incident Command

## Overview

Triage, contain, recover, and review Adobe auth, product, async-job, event, storage, spend, or App Builder incidents with evidence.. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

Vendor status, local deployment, credentials/entitlement, request validity, queues, storage, and downstream systems are separate failure domains. Containment preserves evidence while stopping new harm; recovery never starts with blind retry or credential deletion. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

A suspected secret or signed-URL exposure is a security incident. Add/rotate/deploy/verify before approved old-secret deletion; invalidate exposed temporary access and preserve last-use evidence.

## Instructions

1. Declare severity, commander, service/operation, environment, customer/data/spend impact, and incident clock.
2. Freeze risky deploys/replays and capture content-safe request/job/activation IDs, queue state, artifact revision, and vendor status.
3. Classify local, auth/entitlement, validation/policy, throttling, vendor, event-delivery, storage, or downstream failure.
4. Contain via queue pause, circuit, credential rotation, registration disablement, or traffic rollback according to owner authority.
5. Recover with one bounded synthetic canary, reconcile ambiguous jobs/events/assets, and restore traffic in stages.
6. Verify data/spend/cleanup, communicate status, preserve timeline, and assign corrective actions with evidence.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Commander coordinates; security authorizes secret response; product/data/budget owners authorize replay, generation, transfer, or deletion; release owner authorizes rollback/redeploy.

## Error Handling

- Do not delete the only credential during containment.
- Do not replay unknown PDF/Firefly jobs without reconciliation.
- Do not declare recovery from endpoint health alone.

## Output

Return severity, timeline, evidence, fault domain, containment, recovery tests, reconciliation, customer/data/spend impact, and follow-ups. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Contain a synthetic leaked secret with overlap rotation.
- Recover a queue after vendor 429s without duplicate submissions.

## Validation

Exercise and record expected and observed results for:

- credential exposure
- entitlement loss
- 429 storm
- unknown jobs
- event disablement
- rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
