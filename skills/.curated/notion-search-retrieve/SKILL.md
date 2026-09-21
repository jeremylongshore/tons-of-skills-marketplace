---
name: notion-search-retrieve
description: >-
  Analyze search intent and retrieve explicitly shared Notion pages or data sources while respecting search limitations and object identity. Use when locating content before a scoped read. Trigger with "search Notion", "find Notion page", or "retrieve Notion content".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<query> <object-type> <retrieval-depth>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, search]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Search and Retrieval Workflow

## Overview

Analyze search intent and retrieve explicitly shared Notion pages or data sources while respecting search limitations and object identity.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Current search returns shared pages and data sources, is title-oriented, paginated, and not guaranteed to reflect changes immediately. A specific structured dataset should be queried through its data-source endpoint instead. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Use read capability and an approved shared-content scope. User fields and page bodies need separate minimization decisions.

## Instructions

1. Clarify whether the operator knows an exact ID, title fragment, database, or data-source identity.
2. Prefer exact-ID retrieval when provenance exists; otherwise run a type-scoped paginated search.
3. Record every page of candidates and disambiguate by object type, parent, and stable ID.
4. Retrieve only approved metadata, properties, blocks, or markdown required by the task.
5. Recursively traverse blocks only when requested and with depth, page, and byte bounds.
6. Return completeness limits, access gaps, and the selected object's evidence.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require the content owner before reading page bodies, user information, sensitive properties, descendants, or files beyond the approved scope.

## Error Handling

- Do not interpret no search result as proof that content does not exist.
- Do not use a database ID as a data-source query target.
- Stop recursive retrieval at the approved depth or byte budget.

## Output

Return the search plan, paginated candidates, chosen stable IDs, retrieval manifest, truncation, access gaps, and evidence date. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Disambiguate two pages with the same title using parent and ID.
- Retrieve a page's approved blocks without following unrelated links.

## Validation

Exercise and record these paths with expected and observed results:

- pagination
- duplicate title
- index lag
- unshared content
- nested blocks
- byte bound

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
