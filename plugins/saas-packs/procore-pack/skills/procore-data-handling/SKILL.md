---
name: procore-data-handling
description: >-
  Transfer Procore documents, images, and attachments through the documented upload and secure-download contracts with checksums, bounded retention, and resource association. Use when importing, exporting, or migrating construction files. Trigger with: "upload a file to Procore", "download Procore documents securely", "migrate Procore attachments".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[file-operation-and-resource-type]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - files
  - data-governance
compatibility: 'Requires approved source files, Procore resource permissions, encrypted temporary storage, and checksum-capable transfer tooling.'
---

# Procore Governed File Transfer

## Overview

Treat file bytes, upload sessions, returned storage instructions, resource association, and secure downloads as separate contracts. Never infer a permanent public URL or place customer documents in logs or diagnostic bundles.

## Prerequisites

- Approved company, project, target resource, file classification, and retention period
- Current upload or document endpoint selected for the resource and file size
- OAuth principal with required tool access and encrypted staging storage

## Instructions

### Step 1: Inventory the transfer

Record source checksum, media type, size, logical owner, target resource, and duplicate policy. Reject unsupported or unclassified content before upload.

### Step 2: Choose the documented flow

Use the current direct, segmented, unified, or resource-specific upload sequence documented for the target. Do not reuse a legacy upload contract merely because it returns an identifier.

### Step 3: Upload to provider storage

Follow the returned storage request exactly, including method, fields, segment ordering, and completion step. Never send the Procore Bearer token to an unrelated storage host unless documentation explicitly requires it.

### Step 4: Associate the upload

Use the documented upload identifier or attachment-by-reference shape for the target resource. Reconcile the resource after association.

### Step 5: Download securely

Treat returned file URLs as opaque and potentially changing. Supply the Bearer token where secure-file guidance requires it and avoid persisting signed or redirect URLs.

### Step 6: Verify and expire

Compare checksums or an approved content assertion, record association IDs, then remove temporary bytes and URLs according to retention policy.

## Authentication

Procore resource and secure-file requests use an OAuth 2.0 Bearer token and required company context. Storage-upload authorization follows the provider-returned upload contract; do not leak the Procore token across hosts.

## Tool Discipline

Use Read and Grep to inspect file metadata, endpoint contracts, and retention rules. Use Write or Edit only for the approved transfer adapter, manifest, test, or redacted receipt; never write customer bytes into source control.

## Output

- Transfer and classification manifest
- Upload, association, download, and checksum evidence
- Temporary-storage deletion and retention receipt

Return identifiers and hashes, not file contents or signed URLs.

## Examples

A drawing import creates the documented upload session, sends bytes to the returned storage destination, completes the upload, associates its upload ID with the target resource, verifies the resulting metadata, and deletes the encrypted staging copy.

## Error Handling

| Failure | Response |
| --- | --- |
| Storage upload fails | Preserve the upload-session reference and retry only as that contract permits. |
| Association returns 422 | Validate target resource, upload ID, and endpoint-specific body without re-uploading blindly. |
| Download URL changes or redirects | Treat it as opaque and follow current secure-file guidance. |
| Checksum or content assertion fails | Quarantine the result and do not publish it downstream. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Direct file uploads](https://developers.procore.com/documentation/tutorial-uploads)
- [Secure file access](https://developers.procore.com/documentation/secure-file-access-tips)
- [File attachments and image uploads](https://developers.procore.com/documentation/tutorial-attachments)
