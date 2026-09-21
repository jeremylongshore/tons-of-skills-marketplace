---
name: mistral-debug-bundle
description: >-
  Assemble a content-free Mistral diagnostic bundle with hashes, schema facts, and explicit exclusions. Use when escalating a persistent integration problem. Trigger with "build a Mistral debug bundle", "prepare Mistral support evidence", or "sanitize Mistral diagnostics".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<incident-id> <time-window> <output-directory>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, diagnostics]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral Sanitized Diagnostic Bundle

## Overview

Produce minimum reproducible evidence without exporting credentials, prompts, responses, files, embeddings, personal data, or unbounded logs.

## Prerequisites

- An incident ID, bounded UTC window, and approved local destination.
- A redaction policy and independent reviewer.
- Known application version, client pin, environment, and endpoint class.

## Current Contract

Useful diagnostics are structural: timestamps, statuses, request IDs, versions, attempts, latency, usage totals, state transitions, and config presence. Raw bodies are excluded by default.

## Authentication

Represent auth only as secret-reference presence, expected host, and key-age class. Exclude keys, headers, secret-derived fingerprints, and secret-manager payload.

## Instructions

1. Create an allowlisted manifest and prohibited-content list before collection.
2. Gather version pins, deployment identity, endpoint/model, normalized parameters, and flags.
3. Aggregate statuses, latency, usage, retries, and transitions within the window.
4. Hash approved config/schema files only after removing secret-bearing fields.
5. Scan the staged bundle for credentials, content, personal data, URLs, and file bytes.
6. Obtain reviewer approval of manifest and exclusions before submission.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Invocation permits only local preparation. Production log queries, identifiers, support contact, upload, and extended retention need approval.

## Error Handling

- Recursive log export can create a second incident.
- Hashing a key still creates a secret-derived identifier.
- Provider request IDs may be sensitive and require review.

## Output

Return bundle path, manifest hash, range, included classes, exclusions, scanner result, reviewer, retention deadline, and submission state.

## Examples

- Package a manifest, lock excerpt, aggregate counts, and redacted schema.
- Report `raw_content=excluded; scanner=pass; submission=not-authorized`.

## Validation

Open every staged file, compare to the allowlist, scan secrets/content, verify hashes, and test extraction before review.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
