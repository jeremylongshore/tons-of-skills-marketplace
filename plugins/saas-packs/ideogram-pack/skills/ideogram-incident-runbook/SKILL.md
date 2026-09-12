---
name: ideogram-incident-runbook
description: >-
  Contain Ideogram incidents involving credentials, billing, throttling, unsafe output, webhook loss, asset expiry, or storage failure. Use when coordinating production response and recovery. Trigger with "Ideogram incident", "contain an Ideogram outage", or "recover missing Ideogram images".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<incident-id> <symptom> <environment>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, incident-response]
model: inherit
effort: high
compatibility: "Designed for Claude Code; operational mutations require the incident commander's approval"
---
# Ideogram Incident Response

## Overview

Stabilize an Ideogram integration before chasing image quality or replaying paid requests. Preserve evidence, reduce blast radius, reconcile accepted work, protect sensitive media, and choose recovery actions by incident class.

## Prerequisites

- Incident commander, environment, start time, impact statement, and communication channel.
- Read access to content-free application, queue, vendor-status, webhook, polling, storage, and billing evidence.
- Known controls for admission, concurrency, key revocation, traffic rollback, queue drain, and publication stop.

## Current Contract

Incidents commonly cross separate boundaries: server-side `Api-Key`, prepaid shared team credit, default in-flight capacity, async `generation_id`, signed but non-guaranteed webhook delivery, item safety, expiring URLs, and application storage. Recovery must not collapse these into a generic retry.

## Authentication

Never paste the API key into incident chat or commands. Verify secret provenance through metadata; if exposure is credible, stop new traffic, revoke under owner approval, rotate consumers, and audit historical leakage.

## Instructions

1. Declare severity, impact, affected environment and tenants, known time window, and incident commander.
2. Freeze risky deployments and broad retries; preserve sanitized statuses, identifiers, queue state, and storage receipts.
3. Classify credential, depleted credit, validation, `429` pressure, vendor capacity, unsafe publication, webhook loss, expired URL, or storage failure.
4. Contain with the smallest control: close admission, reduce concurrency, stop publishing, switch to polling, isolate storage, or roll back traffic.
5. Reconcile every accepted async identifier before resubmission and prevent duplicate asset publication.
6. Recover with synthetic canaries, then restore bounded traffic while monitoring safety, durable completion, errors, latency, and spend.
7. Record timeline, decisions, evidence, customer impact, cleanup, follow-ups, and final state.

## Tool Discipline

Use Read, Glob, and Grep for evidence and known runbooks. Use Write and Edit for approved incident records or fixes. Do not revoke keys, add credit, delete assets, replay jobs, or deploy without incident authority.

## Approval Boundaries

The incident commander approves containment and restoration; security owns credential response, billing owns credit, moderation owns unsafe publication, and data owners approve asset access or deletion. Separate reversible mitigation from destructive action.

## Error Handling

- Do not regenerate solely because a vendor URL expired; confirm rights, budget, and absence of durable copy.
- Do not increase concurrency during `429` pressure.
- Missing webhook delivery should trigger polling reconciliation, not duplicate submission.

## Output

Return incident class, impact, timeline, evidence IDs, containment, accepted-work reconciliation, spend and data exposure, recovery canary, owners, residual risk, and rollback or cleanup state. Exclude secrets and content.

## Examples

- On webhook loss, keep submissions bounded, poll known generation IDs, and deduplicate late deliveries.
- On unsafe publication, stop the publisher while preserving the generation and safety decision evidence.

## Validation

Confirm impact has stopped, all known generations and objects reconcile, synthetic canaries pass, and monitoring remains stable through the observation window. Test that rollback and emergency admission closure still work.

## Resources

- [Current first-party evidence map](references/official-docs.md)
