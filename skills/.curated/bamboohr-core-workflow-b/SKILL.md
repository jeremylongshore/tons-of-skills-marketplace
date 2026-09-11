---
name: bamboohr-core-workflow-b
description: >-
  Govern BambooHR time-off, benefit, and employee-file operations with explicit
  read/write separation and HR approval. Use when integrating leave balances,
  benefit membership, or protected employee documents. Trigger with "BambooHR
  time off", "BambooHR benefits", "BambooHR files", or "BambooHR PTO".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<time-off|benefits|files> <read|propose-write>"
version: 1.5.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, hr, bamboohr, time-off, benefits, files]
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# BambooHR Time-Off, Benefits, and Files

## Overview

Implement sensitive secondary HR workflows without collapsing reads and
mutations into one privilege boundary. Each domain has different approvers,
retention needs, and consequences; choose exactly one operation class per run.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The tenant, identity, and data scope only when approved live work is in scope.
- The current evidence register plus customer-specific permissions and agreements.

## Current Contract

The official SDK/OpenAPI exposes time-off policy, balance, request, and status
operations; company and employee benefit reads; and company/employee file
operations. Some operations return an empty body or plain text, so success must
be determined from the documented status and follow-up read—not a guessed JSON
shape.

## Authentication

Use an OAuth client or dedicated API-key user whose permissions match the chosen
domain and action. A file reader should not inherit time-off approval rights; a
balance reader should not inherit employee-file access.

## Instructions

1. Classify the request as time-off, benefits, or files and as read or mutation.
   Record tenant, employee identifier, purpose, approver, and expected effect.
2. Discover IDs from authorized list operations; never accept an unqualified ID
   from another tenant or infer a benefit, policy, request, or file identifier.
3. For reads, request only needed date range, fields, and records. Do not retain
   file bytes or dependent/benefit data in general application logs.
4. For a proposed mutation, generate a before/after preview and idempotency key.
   Validate policy, effective dates, units, status transition, and employee.
5. Obtain approval from the owning HR role immediately before execution. Re-read
   the target after approval to detect intervening changes.
6. Verify status and state with a follow-up read. Record request ID and audit
   metadata, not raw employee data.
7. Define compensation for partial failure; never auto-reverse an approved HR
   action without a second authorization.

## Tool Discipline

Use Read, Glob, and Grep to inspect domain mappings and current safeguards. Use
Write/Edit only for approved adapters, previews, and tests. The allowed tools do
not authorize a live BambooHR read, download, or mutation.

## Approval Boundaries

Require separate approval for any time-off request/status change, balance
adjustment, benefit write, file upload/download/delete, or permission expansion.
Never expose document contents in a chat transcript or CI artifact.

## Output

Return domain, operation, tenant, minimized inputs, before/after preview,
approval identity, response status, verification read, request ID, retention
handling, and rollback or compensation status.

## Error Handling

- `403`: report the exact operation and permission boundary.
- `409` or `412`: stop on state/policy conflict and refresh the preview.
- Empty success body: use documented status and follow-up state.
- Partial file transfer: discard the incomplete file and do not retry a write
  until idempotency is established.

## Examples

- "Show approved PTO next week" stays a time-bounded read.
- "Approve this request and upload the doctor's note" becomes two independently
  approved operations with different evidence and retention controls.

## Resources

Read [official evidence](references/official-docs.md) before choosing an operation.
