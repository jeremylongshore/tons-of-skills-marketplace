# Crypto News Aggregator Plugin

Fetch cryptocurrency RSS feeds on demand with coin/category filters and per-source health reporting.

## Features

- Multi-source aggregation
- Keyword and recency scoring
- UTC publication-date filtering
- Table, JSON and CSV output
- Explicit partial-failure and disabled-feed diagnostics

## Implemented transport boundaries

Feeds use an isolated Requests session with environment proxy, netrc and environment CA overrides disabled. TLS verification remains enabled. Initial URLs and each redirect must use HTTPS on the default port without embedded credentials; at most three redirects are followed, with cookies cleared before each request.

Received and cached feed text is parsed as an in-memory data stream, never as a URL or local filename.

Responses stream into a bounded buffer (2 MiB by default, also checked after text decoding). Oversized responses, redirect failures and read-deadline expiry appear as failed-feed receipts and are not cached as successful results. Cache reads are bounded too. Socket inactivity timeouts and application deadline checks between yielded chunks are enforced. DNS resolution and slow trickling within a chunk are not bounded by a hard total wall-clock deadline.

Configured hosts remain operator-trusted. This is not a DNS/IP egress filter or a privacy/compliance certification. Corporate proxy and custom CA environments need a separately reviewed configuration path rather than implicit credential or trust loading. Public network access still requires the repository's scoped security review.

## Installation

```bash
/plugin install crypto-news-aggregator@claude-code-plugins-plus
```

## Commands

| Command           | Description           | Shortcut |
| ----------------- | --------------------- | -------- |
| `/aggregate-news` | Aggregate crypto news | `an`     |

---

_Built by Intent Solutions IO_
