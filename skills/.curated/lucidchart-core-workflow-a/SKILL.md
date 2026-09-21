---
name: lucidchart-core-workflow-a
description: 'Create and verify a Lucidchart document through the documented Standard Import REST workflow. Use when generating a diagram from governed data. Trigger with "create Lucid document".'
argument-hint: "[spec-path] [destination-folder]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, lucidchart, rest-api, standard-import, diagrams]
model: inherit
effort: medium
compatibility: Designed for Claude Code; document creation requires an authorized Lucid token and approval from the source-data and destination-folder owners
---
# Governed Lucid Standard Import

## Overview

Transform an approved diagram specification into a deterministic `.lucid` archive, create the document, verify it, and retain rollback evidence.

## Prerequisites

- An approved diagram specification with data classification and owner
- A destination product and folder
- An authorized API key or OAuth user token with the exact create-document scope

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect specifications and fixtures, `WebFetch` for current Standard Import and operation contracts, and `Write` or `Edit` for the local archive source and receipt only.

## Current Contract

- A Standard Import file is a ZIP with required `document.json`, at least one page, and unique item IDs.
- Creation uses the documented multipart endpoint with file, product, and optional title or parent.
- The format evolves, so a previously valid archive may render differently later.

## Authentication

Use Bearer authorization with an approved API key or OAuth user token accepted by the operation. Never print the token. Validate token type, scope, destination access, and current document API version before mutation.

## Instructions

1. Freeze the input specification, intended product, folder, title, ownership, and rollback plan.
2. Build `document.json` and any `/data` or `/images` assets with unique stable IDs and safe relative paths.
3. Validate JSON, ZIP structure, uncompressed sizes, media types, referential integrity, and deterministic ordering locally.
4. Present a mutation preview including document count, pages, shapes, lines, data rows, images, and destination.
5. After approval, submit one idempotency-controlled creation request using exact documented headers and multipart fields.
6. Capture the returned identity without tokens, then retrieve or export only as permitted to verify representative content.
7. Record source digest, created ID, owner, verification, cleanup or retention decision, and rendering variance.

## Approval Boundaries

Do not upload restricted source data, overwrite an existing document, guess a folder, or create duplicates after an ambiguous timeout.

## Output

Return source digest, archive validation, mutation preview, created document ID, verification, rendering variance, owner, and rollback or cleanup.

## Error Handling

| Condition | Response |
|---|---|
| Create response is ambiguous | Reconcile by receipt and destination before retrying. |
| Import rendering differs | Preserve the archive and document ID, report variance, and avoid silent repair. |
| Asset exceeds a documented limit | Reduce or externalize it; do not bypass validation. |

## Example

```text
product=lucidchart; pages=2; shapes=14; archive-sha256=...; created=document-redacted; verification=pass; duplicates=0
```

## Resources

- [Official documentation map](references/official-docs.md)

## Next Steps

Add the validated archive to CI fixtures and document its ownership and regeneration command.
