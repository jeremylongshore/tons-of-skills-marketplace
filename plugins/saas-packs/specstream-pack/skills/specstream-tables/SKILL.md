---
name: specstream-tables
description: |
  Design and validate SpecStream Deep Search table requests for multi-row structured web datasets with quote-before-spend approval and per-value source provenance. Use when collecting many matching entities, enriching a list, or auditing get_find_decisions provenance. Trigger with "SpecStream Deep Search", "build a SpecStream table", or "quote SpecStream list".
argument-hint: "[table-request.json]"
allowed-tools: Read, Bash(python3:*)
version: 1.0.0
author: Tarek Etman <tarek@specstream.ai>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, specstream, deep-search, tables, structured-data]
---
# SpecStream Deep Search Tables Workflow

## Overview

Plan, quote, and validate multi-row structured tables using SpecStream Deep Search. Unlike single-fact web search, Deep Search compiles a plain-language request into columns, prices the ceiling in advance (5c, 15c, or $1 per row, plus 5c/email and 15c/phone when requested), and attaches a `source_url` and `seen_at` read time to every delivered value.

## Prerequisites

- A plain-language specification of the entities, columns, and matching conditions required.
- Either a SpecStream account (MCP `compile`, `quote_capacity_work`, `authorize_capacity_work`, `get_find_decisions`, `replay_find_decisions`) or keyless per-request payment via `POST https://api.specstream.ai/v1/agent/lists` (`count` 1 to 500) using MPP or x402 `upto`.
- Python 3.10+ to validate table payloads offline against [the Deep Search tables contract](references/api-contract.md).

## Instructions

1. Use `Read` to examine the user's target schema, list specification, or existing table JSON and review [the Deep Search tables contract](references/api-contract.md).
2. Confirm whether the workload fits Deep Search tables (multi-row structured collection, list enrichment, or condition-verified rows) rather than a single Search API lookup (`GET /v1/web-search`).
3. Validate the table request and spend-confirmation structure offline before quoting or authorizing spend:

```bash
python3 scripts/validate_specstream_payload.py --kind table --file table-request.json
```

4. On an account, follow the five-step approval flow: `compile` -> `quote_capacity_work` (quotes expire after 30 minutes) -> ask the user to approve the maximum -> `authorize_capacity_work` with `confirm_max_cents` and a stable idempotency key -> inspect results with `get_find_decisions`.
5. Without an account, send `POST /v1/agent/lists` to inspect the `402` column read-back and ceiling before submitting MPP (`Authorization: Payment`) or x402 `upto` (`PAYMENT-SIGNATURE`), and check `GET https://specstream.ai/data/lists.json` first if a pre-built catalog list already exists.

## Output

Return the validated table specification, quote/approval boundary (`confirm_max_cents` and quote TTL), provenance verification plan (`source_url` and `seen_at` via `get_find_decisions` or `replay_find_decisions`), and offline validator result.

## Error Handling

| Condition | Response |
| --- | --- |
| `402 Payment Required` on `/v1/agent/lists` | Expected quote response containing column interpretation, ceiling price, `WWW-Authenticate: Payment` (MPP), and `PAYMENT-REQUIRED` (x402 `upto`). |
| Quote older than 30 minutes | Re-run `quote_capacity_work` before calling `authorize_capacity_work`. |
| Ambiguous or unsupported conditions from `compile` | Surface them to the user and refine the plain-language request before pricing. |
| `confirm_max_cents` missing or mismatched | Stop before authorization; never submit an unapproved spending cap. |

## Examples

**Example 1: Validate a keyless agent list request (count 1 to 500)**

```bash
# Limit to 50 rows for initial quote preview via /v1/agent/lists
python3 scripts/validate_specstream_payload.py --kind table --stdin <<'EOF'
{"request": "US clinical trials recruiting Phase 3 oncology studies", "count": 50}
EOF
```

**Example 2: Validate an account-authorized capacity payload**

```bash
# confirm_max_cents=1500 sets a $15.00 maximum approved ceiling for the quote
python3 scripts/validate_specstream_payload.py --kind table --stdin <<'EOF'
{"request": "Series A robotics startups in Germany with founder emails", "quote_id": "q_example", "confirm_max_cents": 1500}
EOF
```

## Resources

- [Deep Search tables contract](references/api-contract.md)
- [SpecStream Deep Search](https://specstream.ai/deep-search)
- [SpecStream Lists Catalog JSON](https://specstream.ai/data/lists.json)
