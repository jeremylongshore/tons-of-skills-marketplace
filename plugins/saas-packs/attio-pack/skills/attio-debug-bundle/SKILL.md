---
name: attio-debug-bundle
description: >-
  Assemble a minimal redacted Attio diagnostic bundle with request fingerprints, schema context, retry evidence, and environment metadata. Use when escalating an Attio integration failure without leaking CRM data or secrets. Trigger with "Attio debug bundle", "Attio support evidence", or "collect Attio diagnostics".
argument-hint: "[repository-path] [incident-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- attio
- diagnostics
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# Redacted Attio Diagnostic Bundle

## Overview

This skill collects the smallest evidence needed to reproduce or escalate an Attio API problem. Redaction and content review happen before a bundle is written or shared.

## Prerequisites

- A named incident, repository, and failing operation
- Redaction rules for tokens, webhook secrets, IDs, and personal data
- The exact endpoint reference and expected request shape
- An approved destination for the final bundle

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect configuration names, client code, existing logs, and tests without opening secret files unnecessarily. Use `WebFetch` only for current official Attio documentation. Use `Write` or `Edit` only for a reviewed redacted artifact in the approved path.

## Current Contract

- Collect path templates, not customer-bearing URLs.
- Preserve status, content type, documented error fields, retry timing, and pagination mode.
- Record scope names but never token values.
- Do not dump entire records, attribute values, environment variables, headers, or webhook payloads.

## Authentication

If a bounded reproduction is approved, use the existing Bearer credential in process memory. The bundle may state credential type, workspace alias, and granted scopes; it must not contain the credential or reusable signature material.

## Instructions

1. Define the incident question and minimum evidence fields before collection.
2. Inventory the local caller, endpoint path template, method, timeout, retry policy, and pagination mode.
3. Capture one redacted failure fingerprint and one bounded control request if safe.
4. Add object or list schema identifiers only when needed to explain validation behavior.
5. Scan the candidate bundle for token patterns, authorization headers, webhook secrets, record values, emails, phone numbers, and full IDs.
6. Review the redacted output manually, then write the approved bundle and checksum.

## Approval Boundaries

Do not run broad workspace enumeration for diagnostics, collect raw CRM responses, or transmit a bundle until its exact contents and destination are reviewed.

## Output

Return a bundle manifest, redaction report, request fingerprint, observed-versus-expected contract, reproduction result, checksum, and sharing disposition.

## Error Handling

| Condition | Response |
|---|---|
| Secret pattern is found | Stop, redact, and rescan from the beginning. |
| Evidence contains personal data | Replace it with typed placeholders or counts. |
| Reproduction would mutate data | Use fixtures or request explicit disposable-target approval. |
| Bundle does not answer the incident question | Remove noise and collect only the missing field. |

## Examples

Input:

```text
incident=attio-query-429; endpoint=/v2/objects/:object/records/query
```

Expected handoff:

```text
bundle=redacted; secrets=0; fingerprint=complete; sharing=approved
```

This result makes the escalation artifact useful without exporting customer records.

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [REST API overview](https://docs.attio.com/rest-api/overview)
- [Rate limiting](https://docs.attio.com/rest-api/guides/rate-limiting)
- [Authentication](https://docs.attio.com/rest-api/guides/authentication)
