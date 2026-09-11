---
name: lucidchart-hello-world
description: 'Build a minimal valid Standard Import archive and optionally create one Lucidchart document as an approved smoke test. Use when verifying Lucid API access for the first time. Trigger with "Lucidchart hello world".'
argument-hint: "[output-directory]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, lucidchart, quickstart, standard-import, smoke-test]
model: inherit
effort: low
compatibility: Designed for Claude Code; optional live document creation requires an approved Lucid credential and destination
---
# Minimal Lucid Standard Import Smoke Test

## Overview
Create the smallest deterministic `.lucid` fixture, validate it offline, and optionally upload exactly one disposable Lucidchart document after approval.

## Prerequisites
- A clean output directory and current Standard Import documentation
- For live mode, an approved API key or OAuth user token, product, destination, and cleanup owner
- No production or sensitive data

## Tool Discipline
Use `Read`, `Glob`, and `Grep` to inspect local examples, `WebFetch` for the current import and operation contract, and `Write` or `Edit` only for the fixture and redacted receipt.

## Current Contract
A `.lucid` Standard Import file is a ZIP containing `document.json`. It needs at least one page and unique item IDs. Product selection distinguishes Lucidchart from Lucidspark.

## Authentication
Offline validation needs no credential. Live creation uses approved Bearer authorization and any required current version header. Never persist or echo the token.

## Instructions
1. Re-fetch the Standard Import overview and exact create-document operation before coding.
2. Write a deterministic `document.json` with one Lucidchart page, one simple shape, stable unique IDs, and no external assets.
3. Package it as a ZIP with `document.json` at the archive root; record its SHA-256 digest.
4. Validate JSON, members, paths, compression, IDs, product, page count, and uncompressed size offline.
5. Default to stopping here and report the reusable fixture.
6. For live mode, present destination, title, one-document mutation, credential class, verification, and deletion plan.
7. After approval, create once, capture the redacted ID, verify representative content, and delete only if cleanup was approved.

## Approval Boundaries
Do not upload automatically, reuse an ambiguous request, write to a guessed folder, or use real customer data in a hello-world fixture.

## Output
Return mode, fixture path, digest, structural checks, planned or created document ID, verification, and cleanup status.

## Error Handling
| Condition | Response |
|---|---|
| Archive is structurally invalid | Stop before authentication and report the exact member or JSON failure. |
| Upload response is ambiguous | Reconcile the destination before any retry. |
| Cleanup is not approved | Leave the document, record its owner and ID, and do not delete it. |

## Example
```text
mode=offline; product=lucidchart; pages=1; shapes=1; archive-sha256=...; live-mutations=0
```

## Resources
- [Official documentation map](references/official-docs.md)

## Next Steps
Promote the offline fixture into CI before attempting broader imports or extension work.
