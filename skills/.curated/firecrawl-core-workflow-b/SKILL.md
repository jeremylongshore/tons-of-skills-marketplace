---
name: firecrawl-core-workflow-b
description: >-
  Combine Firecrawl v2 map, search, batch scrape, parse, and structured JSON extraction into a governed acquisition workflow. Use when the URL set is unknown or typed data is required. Trigger with "Firecrawl map", "Firecrawl batch", "structured Firecrawl extraction", or "parse a file".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<source-or-query> [map|search|batch|parse|json]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, discovery, extraction]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Discovery and Structured Extraction

## Overview

Discover first, select deliberately, and retrieve only the sources required for the outcome. Separate URL discovery from content acquisition and validate all model-produced JSON.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Use map for site URLs, search for web discovery, batchScrape or startBatchScrape for known URL sets, and parse for local/non-public file bytes. In v2, structured extraction is a json format object with prompt and optional JSON Schema; the legacy extract format name is not the current scrape contract.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Define the research question, approved domains, recency, maximum results/pages, required fields, JSON Schema, and evidence-retention policy.
2. Use map for an owned site or search for broader discovery. Store normalized URLs and source metadata, not content, until selection policy passes.
3. Filter duplicates, unsupported schemes, disallowed domains, and unnecessary query variants. Require review for sensitive or authenticated sources.
4. Choose batchScrape for known URLs and startBatchScrape when work must be asynchronous. Retrieve all required pages through getBatchScrapeStatus pagination.
5. For local PDF, DOCX, XLSX, HTML, or other supported bytes, use parse rather than inventing a public URL. Apply file-size and classification gates first.
6. For typed extraction, request the v2 json format with the narrowest schema and prompt. Treat output as untrusted model data and validate types, constraints, provenance, and completeness.
7. Return discovery, selection, retrieval, validation, cost, and failure receipts as separate stages so partial results are auditable.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before broad web search, uploading non-public files, using LLM-backed extraction on sensitive content, increasing batch size, or retaining raw source content.

## Output

Return the discovery set, selection rationale, chosen v2 operation, job/pagination state, schema validation results, source provenance, rejection reasons, and redacted cost/evidence receipt.

## Error Handling

- Discovery returns too many URLs: tighten search/path policy before retrieval.
- JSON extraction is invalid or prompt-injection protection blocks it: quarantine and require review; never coerce silently.
- Parse input is unsupported or oversized: stop before upload and choose an approved preprocessing path.

## Examples

- "Find and extract product pages" maps or searches, filters URLs, then runs a bounded typed batch.
- "Parse this private PDF" checks classification and approval before uploading bytes to /v2/parse.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
