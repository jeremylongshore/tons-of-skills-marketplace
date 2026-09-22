---
name: clari-core-workflow-b
description: >-
  Extract Clari Copilot calls, details, users, topics, and scorecards into a governed analytics flow. Use when building conversation or coaching datasets. Trigger with: "export Clari Copilot calls", "build conversation analytics", "load Copilot scorecards".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[workspace-time-window-and-dataset]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - clari
  - copilot
  - conversation-intelligence
  - analytics
compatibility: 'Requires entitlement to the Clari conversation-intelligence API, workspace integration credentials, and approval to process recordings, transcripts, and participant data.'
---

# Clari Copilot Conversation Intelligence Extraction

## Overview

Treat Copilot as a separate data product rather than an extension of Revenue API exports. Build a metadata-first extraction that minimizes sensitive content, joins stable identifiers, and records the exact window and pagination boundary.

## Prerequisites

- Copilot API key/password pair stored in an approved secret manager
- Authorized time window, user population, and data-classification decision
- Destination controls suitable for call and participant data

## Instructions

### Step 1: Inventory the required resources

Choose only the calls, call details, users, topics, scorecards, and templates necessary for the approved use case.

### Step 2: Freeze the extraction window

Record workspace, start and end time, pagination order, and inclusion rules so reruns are deterministic.

### Step 3: Fetch metadata first

List users, topics, scorecard templates, and call summaries before requesting detailed call content.

### Step 4: Retrieve bounded details

Request call details only for selected call IDs, honor both documented rate ceilings, and checkpoint pagination without duplicates.

### Step 5: Normalize with privacy controls

Separate identities, call metadata, scoring, and sensitive content; tokenize joins and restrict transcript or recording access.

### Step 6: Reconcile and publish

Compare requested and received IDs, record missing or changed calls, and publish only the authorized dataset with lineage.

## Authentication

Send both `X-Api-Key` and `X-Api-Password` to the Copilot host over HTTPS. Do not substitute the Revenue `apikey`; redact both Copilot credentials and minimize logs containing call titles, participant data, transcripts, or recording links.

## Tool Discipline

Use Read and Grep to inspect configuration, provider contracts, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not issue, rotate, revoke, create, update, cancel, delete, export, ingest, or publish provider data without explicit operator approval.

## Output

- Windowed extraction manifest and pagination checkpoints
- Governed call, user, topic, and scorecard datasets
- Reconciliation, privacy-classification, and publication receipt

Return the exact surface, environment, resource or job identifiers, contract fingerprint, evidence, unresolved risks, and final decision without exposing credentials or sensitive customer data.

## Examples

A coaching dataset lists calls for one approved week, selects only calls for an authorized team, retrieves details under the documented limits, tokenizes participant joins, and records missing IDs before publication.

## Error Handling

| Failure | Response |
| --- | --- |
| One credential header is missing | Stop and validate the Copilot credential pair; do not fall back to a Revenue token. |
| Rate ceiling is reached | Honor retry timing, checkpoint the cursor, and resume without widening concurrency. |
| Detailed content exceeds approval | Publish metadata only and quarantine or omit transcripts and recording references. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Clari Copilot API reference](https://api-doc.copilot.clari.com/)
