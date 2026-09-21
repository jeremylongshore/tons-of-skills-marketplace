---
name: fireflies-data-handling
description: >-
  Audit and govern Fireflies transcripts, summaries, participant data, media links, AskFred output, exports, retention, redaction, and deletion propagation. Use when performing privacy, compliance, or downstream data design. Trigger with "Fireflies data handling", "export Fireflies transcript", or "delete Fireflies data".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, data-governance, privacy]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Meeting Data Governance

## Overview

Govern Fireflies transcripts, summaries, participant data, media links, AskFred output, exports, retention, redaction, and deletion propagation.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

Classify metadata, participants, attendance, sentences, raw_text, summaries, analytics, audio/video URLs, sharing records, webhook payloads, and AskFred answers separately. API access does not override consent, purpose limitation, retention, legal hold, or downstream deletion obligations.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Define the authorized purpose, cohort, fields, recipients, region, retention, and deletion owner.
2. Minimize GraphQL selections and avoid media URLs unless the workflow requires them.
3. Apply deterministic redaction before storage or model use and retain provenance.
4. Encrypt approved stores, separate tenants, and restrict search and export paths.
5. Track copies and derived outputs, including AskFred answers and downstream CRM records.
6. Process access or deletion requests through verified identities and legal-hold checks.
7. Verify deletion propagation and retain only a content-free compliance receipt.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before export, long-term storage, model processing, external sharing, retention changes, media retrieval, or deleteTranscript.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- Consent or purpose is unclear: do not retrieve content.
- Legal hold conflicts with deletion: pause and route to counsel or the data owner.
- Downstream copy cannot be located: stop further propagation and open an incident.

## Examples

- "Review fireflies meeting data governance" produces a bounded plan and redacted receipt.
- A request that widens access or mutates production is paused at the approval boundary.

## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
