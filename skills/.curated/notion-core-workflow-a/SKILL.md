---
name: notion-core-workflow-a
description: >-
  Analyze and query a Notion data source with version-correct filters, pagination, and completeness evidence. Use when retrieving structured workspace records. Trigger with "query Notion data source", "filter Notion records", or "paginate Notion data".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<data-source-id> <filter-intent> <output-scope>"
version: 1.41.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, query]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Data-Source Query Workflow

## Overview

Analyze and query a Notion data source with version-correct filters, pagination, and completeness evidence.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Modern Notion APIs separate the database container from each data source schema. Query operations take a data-source ID; filters and sorts must match that data source's current property schema. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

Opaque cursors are only for the next `start_cursor` request; never parse them or retain them as durable checkpoints or incident evidence.

## Authentication

Use read-content capability and explicit access to the target content. Record the connection alias, not its bearer value.

## Instructions

1. Retrieve database metadata and resolve the intended data-source ID by evidence, not name alone.
2. Retrieve the data-source schema and map requested fields to stable property IDs where practical.
3. Compile and review filters, sorts, page size, and output minimization.
4. Pass each cursor verbatim to the next request and record page counts. Check every response for `request_status.type: incomplete`; `has_more: false` alone does not prove completeness at the 10,000-result query cap.
5. Normalize page property values without assuming every property is populated or returned inline.
6. Reconcile row counts, duplicate IDs, missing pages, and acknowledged output. For full exports, use stable `created_time` windows with inclusive boundaries and record-ID deduplication; refuse nonadvancing or saturated tied boundaries and split further using the official large-source guide. Mutable `last_edited_time` is not a universal full-export checkpoint.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require the data owner before accessing a new data source, user information, sensitive properties, or an export destination.

## Error Handling

- Do not pass a database ID where a data-source ID is required.
- Search is not a substitute for a scoped data-source query.
- Never declare completeness after only the first page.

## Output

Return the resolved IDs, schema revision evidence, filter plan, page ledger, normalized result manifest, and reconciliation totals. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Retrieve all approved task pages with a reviewed status filter.
- Restart an extraction with a fresh query from acknowledged record/time-window progress and deduplicate IDs.

## Validation

Exercise and record these paths with expected and observed results:

- empty result
- multiple pages
- schema drift
- missing property
- duplicate page
- fresh-query restart and nonadvancing window refusal

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- [Cursor lifetime and versioning](https://developers.notion.com/reference/versioning).
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
