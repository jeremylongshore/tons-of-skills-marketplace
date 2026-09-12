---
name: notion-core-workflow-a
description: >-
  Analyze and query a Notion data source with version-correct filters, pagination, and completeness evidence. Use when retrieving structured workspace records. Trigger with "query Notion data source", "filter Notion records", or "paginate Notion data".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<data-source-id> <filter-intent> <output-scope>"
version: 1.40.0
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

## Authentication

Use read-content capability and explicit access to the target content. Record the connection alias, not its bearer value.

## Instructions

1. Retrieve database metadata and resolve the intended data-source ID by evidence, not name alone.
2. Retrieve the data-source schema and map requested fields to stable property IDs where practical.
3. Compile and review filters, sorts, page size, and output minimization.
4. Paginate until the contract says complete while preserving cursors and page counts.
5. Normalize page property values without assuming every property is populated or returned inline.
6. Reconcile row counts, duplicate IDs, missing pages, and the extraction watermark.

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
- Resume a paginated extraction from the last acknowledged cursor.

## Validation

Exercise and record these paths with expected and observed results:

- empty result
- multiple pages
- schema drift
- missing property
- duplicate page
- cursor restart

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
