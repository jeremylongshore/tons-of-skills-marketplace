---
name: specstream-extract
description: |
  Validate and build SpecStream Extract API requests (POST https://api.specstream.ai/v1/extract) for reading live pages, PDFs, Word, Excel, and pre-fetched HTML. Use when extracting clean markdown/text/links or handling per-URL extraction statuses. Trigger with "SpecStream extract", "extract pages with SpecStream", or "validate extract payload".
argument-hint: "[extract-payload.json]"
allowed-tools: Read, Bash(python3:*)
version: 1.0.0
author: Tarek Etman <tarek@specstream.ai>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, specstream, extract, scraping, markdown]
---
# SpecStream Extract API Workflow

## Overview

Build and validate `POST https://api.specstream.ai/v1/extract` calls to extract main text, links, metadata, and emails from up to 20 URLs or pre-fetched HTML pages per call. With an API key, each readable page costs $0.0008 ($0.80 per 1,000 pages) and pages returning no text are not charged.

## Prerequisites

- A list of 1 to 20 public `http`/`https` URLs or pre-fetched HTML `pages` objects (20 MB total request cap).
- Optional `SPECSTREAM_API_KEY` (Bearer token with `finds:spend`) for live calls, or x402 per-call payment when running without an account.
- Python 3.10+ for offline payload validation against [the Extract API contract](references/api-contract.md).

## Instructions

1. Use `Read` to inspect the caller payload or URL batch and verify [the Extract API contract](references/api-contract.md).
2. Confirm `urls` and `pages` combined hold between 1 and 20 items, `format` is `markdown` (default), `text`, or `html`, and `include` only requests supported fields (`full_text`, `html`, `links`, `response`).
3. Add an `Idempotency-Key` header (at most 128 characters) when retrying so repeated requests within 7 days replay with `Idempotent-Replayed: true` and no duplicate charge (note zero-retention keys return `409` on replay).
4. Validate the request JSON offline before sending it:

```bash
python3 scripts/validate_specstream_payload.py --kind extract --file extract-payload.json
```

5. When consuming `data.results`, handle every item's `status` independently (`ok`, `blocked`, `not_found`, `empty`, `unsupported`, `invalid_url`, `failed`) and preserve `read_from` (`live`, `site`, `archive`, `html`) and `captured_at` provenance.

## Output

Return the validated Extract request payload, per-item status handling plan, expected `data.results` fields (`url`, `status`, `text`, `title`, `published`, `modified`, `emails`, `read_from`), and offline validator status. Exclude any credentials from logs.

## Error Handling

| Condition | Response |
| --- | --- |
| `400` | Ensure `urls` and `pages` together contain between 1 and 20 valid items. |
| `401` / `402` / `403` | Check `SPECSTREAM_API_KEY`, balance, monthly cap, `finds:spend` scope, and `spend_cap_cents`. |
| `409` | A charged `Idempotency-Key` was reused without a stored reply (zero-retention key, older than 7 days, or in-flight); send a new key. |
| `422` | Shorten `Idempotency-Key` to 128 characters or fewer. |
| `503` with `Retry-After` | Wait the indicated seconds before retrying; nothing is charged. |
| Item `status` is `blocked` or `not_found` | Do not treat error page `text` as successful extraction; record the non-charged status (`read_from: archive` is checked automatically for 404/410). |

## Examples

**Example 1: Validate a mixed URL and pre-fetched HTML extract request**

```bash
python3 scripts/validate_specstream_payload.py --kind extract --stdin <<'EOF'
{"urls": ["https://specstream.ai/agents.md"], "format": "markdown", "include": ["links", "response"]}
EOF
```

**Example 2: Check an oversized batch offline (fails with clear error)**

```bash
python3 scripts/validate_specstream_payload.py --kind extract --stdin <<'EOF'
{"urls": []}
EOF
```

## Resources

- [Extract API contract](references/api-contract.md)
- [SpecStream Agent Reference](https://specstream.ai/agents.md)
- [SpecStream Extract API Docs](https://specstream.ai/docs/extract-api)
