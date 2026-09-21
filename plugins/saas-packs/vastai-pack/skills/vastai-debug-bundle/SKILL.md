---
name: vastai-debug-bundle
description: >-
  Collect a minimal, redacted Vast.ai diagnostic manifest that support can act on without exposing API keys, SSH material, workload secrets, or unnecessary customer data. Use when escalating a platform or workload fault. Trigger with: "build a Vast.ai debug bundle", "collect Vast.ai support evidence", "redact Vast.ai diagnostics".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[incident-window-and-resource-ids]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - diagnostics
  - support
  - redaction
compatibility: 'Requires read access to affected Vast.ai resources, an approved evidence location, and a defined incident window.'
---

# Redacted Vast.ai Support Manifest

## Overview

A useful bundle binds exact resource IDs, CLI version, timestamps, states, and redacted errors. It does not archive the entire environment, shell history, account profile, or secret-bearing generated curl commands.

## Prerequisites

- Incident window, affected instance/endpoint/workergroup IDs, and symptom
- Evidence classification, retention period, support case owner, and approved destination
- Redaction rules for API keys, URLs, emails, storage credentials, model inputs, and customer data

## Instructions

### Step 1: Freeze the collection plan

List each command, field, time range, and justification before reading data. Exclude environment dumps and home-directory archives.

### Step 2: Collect control-plane facts

Record CLI version, redacted `show user`, structured instance or Serverless state, offer/template identity, and timestamps.

### Step 3: Collect bounded logs

Retrieve only the relevant container, endpoint, or workergroup log window and filter known credential and payload fields.

### Step 4: Capture request diagnostics safely

Use `--explain` or equivalent call metadata only when the output is reviewed for bearer tokens and query credentials before storage.

### Step 5: Redact and inventory

Replace sensitive values consistently, retain resource IDs needed by support, and create file hashes plus a redaction attestation.

### Step 6: Validate the bundle

Have a second pass search for key patterns, private keys, URLs with credentials, emails, and workload secrets before sharing.

## Authentication

Prefer a read-only scoped key. Never store `VAST_API_KEY`, key-file contents, SSH private material, webhook secrets, cloud credentials, or Authorization headers in the bundle.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Collection scope and command manifest
- Redacted evidence files with hashes and time bounds
- Redaction attestation, retention date, and support handoff receipt

Return incident window, resource IDs, collected fields, excluded classes, file hashes, redaction result, and recipient.

## Examples

A support manifest contains CLI version, one offline instance record, the last 100 redacted log lines, template hash, timestamps, and checksums; it excludes environment variables and generated Authorization headers.

## Error Handling

| Failure | Response |
| --- | --- |
| A secret detector fires | Quarantine the bundle, rotate exposed credentials if necessary, and rebuild from source. |
| Requested data exceeds the incident window | Exclude it unless the case owner documents a need. |
| Resource has already been destroyed | Use retained external receipts; do not fabricate live state. |
| Support asks for raw credentials | Refuse and provide a redacted reproduction instead. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Official CLI global flags](https://github.com/vast-ai/vast-cli/blob/master/vastai/SKILL.md#global-flags)
- [Instance logs command](https://docs.vast.ai/cli/reference/logs)
- [Serverless logging](https://docs.vast.ai/guides/serverless/logging)
