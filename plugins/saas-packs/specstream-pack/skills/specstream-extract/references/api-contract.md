# SpecStream Extract API Reference

## Endpoint and Limits

- `POST https://api.specstream.ai/v1/extract`
- Also available on MCP as `read_pages` (`{"urls": ["<url>", ...]}`) and drop-in routes (`/tavily/extract`, `/exa/contents`, `/firecrawl/v2/scrape`, `/jina`).
- Items: 1 to 20 entries across `urls` and `pages` (`[{"html": "...", "url": "..."}]`), 20 MB request size limit, 30s per URL.
- Pricing: $0.0008 per page read with API key ($0.80 per 1,000 pages); pages returning no text are not charged. Per-call x402 charges $0.002 per requested page.

## Parameters

- `format`: `markdown` (default), `text`, or `html`.
- `include`: array containing any of `full_text`, `html`, `links`, `response`.
- Header `Idempotency-Key`: up to 128 characters, replays within 7 days with `Idempotent-Replayed: true` (returns `409` on zero-retention keys).

## Result Statuses

- `ok`: read and charged.
- `blocked`: refused, bot check, or disallowed by robots.txt (bot check pages are never returned as text).
- `not_found`: 404/410 with no public archive capture.
- `empty`: no main text (not charged with API key).
- `unsupported`: not web page, text, PDF, Word, Excel, EPUB, or image.
- `invalid_url`: not a public `http` or `https` URL.
- `failed`: timeout or transport error.
