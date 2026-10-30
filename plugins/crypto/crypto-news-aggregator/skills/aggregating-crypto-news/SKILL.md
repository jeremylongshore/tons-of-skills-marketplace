---
name: aggregating-crypto-news
description: 'Aggregate cryptocurrency news from configured RSS sources including CoinDesk,
  CoinTelegraph, The Block, and Decrypt.

  Use when needing to monitor crypto market news, track announcements, or find coin-specific
  updates.

  Trigger with phrases like "get crypto news", "latest Bitcoin headlines", "DeFi announcements",
  "scan for breaking news", or "check crypto updates".

  '
allowed-tools: Read, Bash(python:*)
version: 1.27.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
  - crypto
  - monitoring
  - aggregating-crypto
compatibility: Designed for Claude Code
---

# Aggregating Crypto News

## Overview

Fetch configured RSS feeds on demand, filter dated articles by coin/category and UTC time window, and rank them using keyword and recency scores. Source availability and coverage vary; the tool reports failed and disabled feeds rather than implying every source was checked successfully.

## Prerequisites

The user prepares the Python environment before invoking this skill.

1. **Python 3.8+** installed
2. **Dependencies**: `pip install feedparser requests pyyaml`
3. Internet connectivity for RSS feed access

## Instructions

1. **Assess user intent** - determine filters needed:
   - General news: no filters, use defaults
   - Coin-specific: extract symbol (BTC, ETH, etc.)
   - Category-specific: extract category (defi, nft, regulatory, etc.)
   - Time-specific: extract window (1h, 4h, 24h, 7d)

2. **Run the aggregator** with appropriate filters:

   ```bash
   # Default scan (top 20, past 24h, relevance sorted)
   python ${CLAUDE_SKILL_DIR}/scripts/news_aggregator.py

   # Coin-specific scan
   python ${CLAUDE_SKILL_DIR}/scripts/news_aggregator.py --coin BTC --period 4h

   # Category filter
   python ${CLAUDE_SKILL_DIR}/scripts/news_aggregator.py --category defi --top 30

   # Multiple filters
   python ${CLAUDE_SKILL_DIR}/scripts/news_aggregator.py --coin ETH --category defi --period 24h --top 15
   ```

3. **Export results** for downstream processing:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/news_aggregator.py --format json --output news.json
   ```

4. **Present results** to the user:
   - Show source, title, age, and relevance score
   - Highlight market-moving keywords if present
   - Provide links for full articles
   - Summarize configured/disabled, fetched/failed sources and articles found
   - Report feed failures, including when other feeds return matching articles
   - A zero-match query is distinct from an all-feed failure (exit 1)
   - JSON `meta.feed_health` records per-source parsed/window/undated counts and latest publication; CSV keeps diagnostics on stderr
   - Undated and future-dated items are excluded from the requested time window

## Output

Table showing articles ranked by relevance score (0-100) based on market-moving keyword detection, source authority, and recency:

```text
CRYPTO NEWS AGGREGATOR — [generated UTC time]
[rank] [source] [headline] [age] [score]
Summary: [shown] articles | [attempted] sources | [matched] matches
Feed health: [fetched] fetched | [failed] failed | [disabled] disabled
[source]: failed — [HTTP/timeout/parse reason, when applicable]
```

This is a layout example, not a record of actual headlines or coverage. RSS
publication dates govern the time window, not fetch time or a claimed live scan.
The registry retains disabled URLs and dated reasons for review; re-enable a
source only after checking its current feed and any publisher usage terms.

## Error Handling

| Error           | Cause                | Solution                                                |
| --------------- | -------------------- | ------------------------------------------------------- |
| Network timeout | RSS feed unreachable | Uses valid, unexpired cache; reports failures otherwise |
| Parse error     | Malformed RSS        | Skips entry; continues with valid articles              |
| No results      | Filters too strict   | Inspect feed health before suggesting relaxed filters   |
| Invalid coin    | Unknown symbol       | List similar valid symbols                              |

Use Read to inspect [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

Filtering patterns for common news monitoring scenarios:

```bash
# Latest crypto news (defaults)
python ${CLAUDE_SKILL_DIR}/scripts/news_aggregator.py

# Bitcoin news from past 4 hours
python ${CLAUDE_SKILL_DIR}/scripts/news_aggregator.py --coin BTC --period 4h

# DeFi category news
python ${CLAUDE_SKILL_DIR}/scripts/news_aggregator.py --category defi

# High-relevance news only
python ${CLAUDE_SKILL_DIR}/scripts/news_aggregator.py --min-score 70 --top 10

# Multiple coins
python ${CLAUDE_SKILL_DIR}/scripts/news_aggregator.py --coins BTC,ETH,SOL
```

## Resources

- [`references/implementation.md`](references/implementation.md) - CLI options, categories, JSON format, advanced filtering
- [`references/errors.md`](references/errors.md) - Comprehensive error handling
- [`references/examples.md`](references/examples.md) - Detailed usage examples
- `${CLAUDE_SKILL_DIR}/config/sources.yaml` - Full source registry
- CoinDesk RSS: https://www.coindesk.com/arc/outboundfeeds/rss/
- feedparser docs: https://feedparser.readthedocs.io/
