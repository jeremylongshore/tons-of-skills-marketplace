# ARD: Aggregating Crypto News

Implementation status (2026-10-25): the shipped runtime is the on-demand RSS CLI
under `scripts/news_aggregator.py`, with the registry in `config/sources.yaml`.
The original source-count and service/latency targets below are design targets,
not measured coverage or deployed services. Current failure, disabled-source and
UTC-window behavior is documented in [SKILL.md](SKILL.md). AI sentiment, social
APIs and push delivery are not implemented by this CLI.

> Part of [Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)

## Document Control

The document version is independent of plugin and skill release versions.

| Field                    | Value                                        |
| ------------------------ | -------------------------------------------- |
| **Skill Name**           | aggregating-crypto-news                      |
| **Architecture Pattern** | Data Aggregation Pipeline                    |
| **Document Version**     | 2.0.0                                        |
| **Author**               | Jeremy Longshore <jeremy@intentsolutions.io> |

---

## Architectural Overview

### Pattern: Multi-Source Data Aggregation

This skill implements a parallel fetching, aggregation, and filtering pipeline for RSS-based news sources.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CRYPTO NEWS AGGREGATOR ARCHITECTURE                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   RSS Source 1   │     │   RSS Source 2   │     │   RSS Source N   │
│   (CoinDesk)     │     │  (CoinTelegraph) │     │   (The Block)    │
└────────┬─────────┘     └────────┬─────────┘     └────────┬─────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │    FEED FETCHER         │
                    │  (Parallel Requests)    │
                    │  - Timeout handling     │
                    │  - Caching layer        │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    FEED PARSER          │
                    │  - XML/RSS parsing      │
                    │  - Date normalization   │
                    │  - Content extraction   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    DEDUPLICATOR         │
                    │  - Title similarity     │
                    │  - URL matching         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    SCORER               │
                    │  - Keyword matching     │
                    │  - Market-moving boost  │
                    │  - Source quality       │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    FILTER ENGINE        │
                    │  - Time window          │
                    │  - Coin matching        │
                    │  - Category filtering   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    FORMATTER            │
                    │  - Table output         │
                    │  - JSON export          │
                    │  - CSV export           │
                    └─────────────────────────┘
```

### Workflow

1. **Fetch**: Parallel HTTP requests to RSS feeds with timeout handling
2. **Parse**: Extract title, content, date, source from XML
3. **Dedupe**: Remove duplicate articles based on title similarity
4. **Score**: Calculate relevance score based on keywords and source
5. **Filter**: Apply user filters (time, coin, category)
6. **Format**: Output in requested format

---

## Progressive Disclosure Strategy

### Level 1: Simple Scan (Default)

```bash
python news_aggregator.py
```

Returns top 20 news from past 24h, relevance sorted.

### Level 2: Filtered Scan

```bash
python news_aggregator.py --coin BTC --period 4h --top 10
```

Adds coin and time filtering.

### Level 3: Category + Export

```bash
python news_aggregator.py --category defi --format json --output news.json
```

Full filtering with export.

### Level 4: Advanced Configuration

```bash
python news_aggregator.py --sources coindesk,theblock --min-score 50 --verbose
```

Source selection and score thresholds.

---

## Tool Permission Strategy

### Allowed Tools (Scoped)

```yaml
allowed-tools: Read, Bash(python:*)
```

| Tool | Scope        | Purpose                        |
| ---- | ------------ | ------------------------------ |
| Read | Unrestricted | Read config, sources list      |
| Bash | `python:*`   | Execute bundled Python RSS CLI |

### Why These Tools

- **Read**: Load source configuration and settings
- **Bash(python:\*)**: Execute Python scripts for fetching and parsing
- **No Write**: Aggregation is read-only; exports use script file output

---

## Directory Structure

```
plugins/crypto/crypto-news-aggregator/
└── skills/
    └── aggregating-crypto-news/
        ├── PRD.md                    # Product requirements
        ├── ARD.md                    # This file
        ├── SKILL.md                  # Core instructions
        ├── scripts/
        │   ├── news_aggregator.py    # Main CLI entry point
        │   ├── feed_fetcher.py       # Parallel RSS fetching
        │   ├── feed_parser.py        # XML parsing and normalization
        │   ├── scorer.py             # Relevance scoring
        │   └── formatters.py         # Output formatting
        ├── references/
        │   ├── errors.md             # Error handling guide
        │   └── examples.md           # Usage examples
        └── config/
            ├── settings.yaml         # Configuration options
            └── sources.yaml          # RSS source registry
```

---

## Data Flow Architecture

### Input

- User request with optional filters (--coin, --period, --category)
- RSS feed URLs from source registry

### Processing Pipeline

```
Input Request
     │
     ├──► Load sources.yaml
     │         │
     │         ▼
     ├──► Parallel fetch (ThreadPoolExecutor)
     │         │
     │         ▼
     ├──► Parse each feed (feedparser library)
     │         │
     │         ▼
     ├──► Normalize entries to common schema:
     │         {
     │           "title": str,
     │           "url": str,
     │           "source": str,
     │           "published": datetime,
     │           "summary": str,
     │           "category": str,
     │           "relevance_score": float
     │         }
     │         │
     │         ▼
     ├──► Deduplicate by title similarity (>80% match)
     │         │
     │         ▼
     ├──► Score relevance:
     │         - Base score from source quality (1-10)
     │         - Keyword boost (+10 per market-moving term)
     │         - Recency boost (newer = higher)
     │         │
     │         ▼
     ├──► Apply filters:
     │         - Time window (published > now - period)
     │         - Coin match (title/summary contains symbol)
     │         - Category match (source category or keywords)
     │         │
     │         ▼
     └──► Format and output
```

### Output Schema

```json
{
  "articles": [
    {
      "rank": 1,
      "title": "Bitcoin Hits New All-Time High",
      "url": "https://coindesk.com/...",
      "source": "CoinDesk",
      "published": "2026-01-14T10:30:00Z",
      "age": "2h ago",
      "category": "market",
      "relevance_score": 85.5,
      "coins_mentioned": ["BTC"]
    }
  ],
  "meta": {
    "total_fetched": 500,
    "after_dedup": 380,
    "after_filter": 25,
    "sources_used": 12,
    "period": "24h",
    "filters": { "category": "market" }
  }
}
```

---

## Error Handling Strategy

### Error Categories

| Category | Examples                      | Strategy                             |
| -------- | ----------------------------- | ------------------------------------ |
| Network  | Timeout, DNS failure          | Skip source, continue with others    |
| Parse    | Malformed XML, missing fields | Skip entry, log warning              |
| Filter   | Invalid coin symbol           | Warn and proceed with partial filter |
| Export   | File permission denied        | Error with clear message             |

### Graceful Degradation

```
Full Success (all sources)
     │
     ▼
Partial Success (some sources failed)
     │ → Log warnings, return available data
     │
     ▼
Cached Fallback (all sources failed)
     │ → Return cached data with stale warning
     │
     ▼
Complete Failure
     │ → Clear error message with remediation
```

---

## Composability & Stacking

### As a Standalone Skill

- Fully functional for news aggregation
- No dependencies on other skills

### As Data Provider

Skills that can consume news data:

- **market-sentiment-analyzer**: Feed articles for sentiment scoring
- **crypto-signal-generator**: Use news as signal input
- **whale-alert-monitor**: Correlate whale activity with news

### Integration Pattern

```python
# In another skill's script:
from pathlib import Path
import subprocess
import json

def get_news_for_coin(coin: str, period: str = "4h") -> list:
    """Fetch news using crypto-news-aggregator skill."""
    news_script = Path(__file__).parent.parent.parent.parent / \
                  "crypto-news-aggregator/skills/aggregating-crypto-news/scripts/news_aggregator.py"

    result = subprocess.run(
        ["python3", str(news_script), "--coin", coin, "--period", period, "--format", "json"],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        return json.loads(result.stdout).get("articles", [])
    return []
```

---

## Performance & Scalability

### Performance Targets

| Metric                    | Target  | Approach                                    |
| ------------------------- | ------- | ------------------------------------------- |
| Fetch time (50 sources)   | < 10s   | Parallel fetching with ThreadPoolExecutor   |
| Parse time (500 articles) | < 2s    | Efficient XML parsing with feedparser       |
| Memory usage              | < 100MB | Stream processing, no full corpus in memory |

### Optimization Strategies

1. **Parallel Fetching**: Use ThreadPoolExecutor(max_workers=10)
2. **Caching**: Cache responses with 5-minute TTL
3. **Lazy Parsing**: Parse only after filter candidates identified
4. **Early Exit**: Stop processing when --top limit reached

### Scalability Considerations

- **More Sources**: Linear scaling with parallel fetch
- **Higher Volume**: Pagination and streaming for large exports
- **Frequency**: Caching prevents redundant fetches

---

## Testing Strategy

### Unit Tests

| Component   | Test Cases                                           |
| ----------- | ---------------------------------------------------- |
| FeedFetcher | Timeout handling, cache hit/miss, parallel execution |
| FeedParser  | Valid RSS, malformed XML, missing fields             |
| Scorer      | Keyword matching, source quality, recency boost      |
| Formatters  | Table, JSON, CSV output validation                   |

### Integration Tests

- End-to-end with mock RSS server
- Real feeds (selected stable sources)
- Export file validation

### Manual Testing

```bash
# Default scan
python news_aggregator.py

# Coin filter
python news_aggregator.py --coin BTC

# Category filter
python news_aggregator.py --category defi

# Export
python news_aggregator.py --format json --output test.json
```

---

## Security & Compliance

### Security Considerations

- **No Authentication**: RSS feeds are public, no credentials needed
- **Input Validation**: Sanitize coin symbols and category names
- **Output Sanitization**: Escape HTML in article titles/summaries

### Data Privacy

- No user data collected or stored
- No tracking or analytics
- Cached data is ephemeral (5-minute TTL)

### Rate Limiting

- Respect source rate limits (1 req/source/5min default)
- No aggressive crawling
- Caching reduces request volume
