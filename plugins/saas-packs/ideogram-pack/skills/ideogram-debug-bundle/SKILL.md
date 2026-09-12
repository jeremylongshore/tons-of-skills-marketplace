---
name: ideogram-debug-bundle
description: >-
  Assemble a sanitized Ideogram support bundle with contract, status, queue, storage, and deployment evidence. Use when escalating an incident without exposing keys, prompts, images, or temporary URLs. Trigger with "build an Ideogram debug bundle", "sanitize Ideogram evidence", or "prepare an Ideogram support case".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<incident-id> <time-window> <output-path>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, diagnostics]
model: inherit
effort: high
compatibility: "Designed for Claude Code; bundle creation operates on explicitly scoped local evidence"
---
# Ideogram Sanitized Debug Bundle

## Overview

Create the minimum diagnostic package needed to reproduce or escalate an Ideogram problem. Preserve endpoint, schema, status, timing, concurrency, async, safety, and storage facts while excluding the content and credentials that commonly leak through generic support archives.

## Prerequisites

- An incident identifier, bounded time window, affected environment, and bundle recipient.
- Approved local evidence locations and a data-classification owner.
- A redaction policy, maximum bundle size, retention deadline, and deletion owner.

## Current Contract

Useful content-free fields include endpoint family, method, deployment SHA, adapter version, HTTP status, sanitized vendor error class, `generation_id`, async state, `is_image_safe`, URL-present boolean, queue depth, in-flight count, latency, and object-store result. Prompts, uploaded media, generated images, keys, and expiring URLs are not required by default.

## Authentication

Represent authentication as booleans and provenance such as `header_present=true` and `secret_source=production-manager`. Never collect the `Api-Key` value, environment dumps, shell history, request headers, or secret-manager payloads.

## Instructions

1. Define the incident, window, recipient, evidence roots, permitted fields, byte ceiling, and deletion deadline.
2. Use an allowlist schema rather than copying full logs, requests, responses, or environment state.
3. Collect version, endpoint, status, timing, concurrency, queue, safety, polling or webhook, and storage facts.
4. Replace user, object, request, and generation identifiers with stable incident-local tokens unless the recipient explicitly requires an opaque vendor ID.
5. Scan the staged bundle for credential patterns, prompts, URLs, image signatures, EXIF, binary files, and customer identifiers.
6. Write a manifest with hashes, field provenance, redaction counts, limitations, owner, and expiry.
7. Obtain recipient approval, transfer through the approved channel, and record deletion.

## Tool Discipline

Use Read, Glob, and Grep to locate and inspect the approved evidence scope. Use Write and Edit only inside the explicitly named staging directory and manifest. Do not run live calls, expand the time window, scrape home directories, or attach repository secrets.

## Approval Boundaries

Require approval before including raw vendor bodies, opaque production identifiers, customer-derived metadata, or any content. The recipient and expiry must be known before transfer; bundle creation alone does not authorize sharing.

## Error Handling

- Stop if an allowlist field cannot be separated from prompt or image content.
- Reject archives containing `IDEOGRAM_API_KEY`, `Api-Key`, signed URLs, image magic bytes, or unbounded logs.
- If evidence is insufficient, report the missing field instead of broadening collection silently.

## Output

Return bundle path, manifest hash, incident and time scope, file and byte counts, redaction and secret-scan results, recipient, transfer status, expiry, and deletion receipt. Do not echo bundle content into the response.

## Examples

- Include deployment SHA, V4 route, `429` count, peak in-flight count, and retry policy; omit bodies and prompts.
- Report `files=4; secrets=0; images=0; urls=0; recipient=vendor-support; expires=24h`.

## Validation

Open every staged file through the allowlist parser, rerun secret and binary scans, verify hashes after transfer, and test deletion. A compressed archive is not safe merely because it is encrypted.

## Resources

- [Current first-party evidence map](references/official-docs.md)
