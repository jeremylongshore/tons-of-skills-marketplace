# PRD: Aggregating Crypto News

Implementation status (2026-10-25): the shipped runtime is the on-demand RSS CLI
under `scripts/news_aggregator.py`, with the registry in `config/sources.yaml`.
The original source-count and service/latency targets below are design targets,
not measured coverage or deployed services. Current failure, disabled-source and
UTC-window behavior is documented in [SKILL.md](SKILL.md). AI sentiment, social
APIs and push delivery are not implemented by this CLI.

## Document Control

The document version is independent of plugin and skill release versions.

| Field                | Value                                              |
| -------------------- | -------------------------------------------------- |
| **Skill Name**       | aggregating-crypto-news                            |
| **Type**             | Data Aggregation & Information                     |
| **Domain**           | Cryptocurrency News & Media                        |
| **Target Users**     | Traders, Analysts, Researchers, Portfolio Managers |
| **Priority**         | P1 - Foundation Skill                              |
| **Document Version** | 2.0.0                                              |
| **Author**           | Jeremy Longshore <jeremy@intentsolutions.io>       |

---

## Executive Summary

The aggregating-crypto-news skill provides real-time cryptocurrency news aggregation from multiple authoritative sources including RSS feeds, news APIs, and social media. It enables traders and analysts to stay informed about market-moving events, protocol updates, regulatory changes, and ecosystem developments without manually monitoring dozens of sources.

**Value Proposition**: Consolidate crypto news from 50+ sources into a single, filterable feed with relevance scoring and coin-specific filtering.

---

## Problem Statement

### Current Pain Points

1. **Information Overload**: Crypto news is scattered across hundreds of sources - Twitter, Discord, Telegram, news sites, protocol blogs, exchange announcements
2. **Signal vs Noise**: Separating market-moving news from promotional content and spam is time-consuming
3. **Missed Events**: Important announcements (airdrops, forks, delistings) can be missed without constant monitoring
4. **No Central Feed**: No single tool aggregates RSS feeds, Twitter spaces, Discord announcements, and official blogs

### Impact of Not Solving

- Traders miss alpha from early news detection
- Portfolio managers react late to regulatory changes
- Researchers waste hours manually checking sources
- Teams lack shared news intelligence

---

## Target Users

### Persona 1: Active Day Trader

- **Name**: Marcus
- **Role**: Full-time crypto day trader
- **Goals**: Catch news before price moves; identify catalysts
- **Pain Points**: Misses announcements; overwhelmed by noise
- **Usage**: Runs news scan every 30 minutes during active sessions

### Persona 2: Research Analyst

- **Name**: Sarah
- **Role**: Crypto research analyst at investment firm
- **Goals**: Comprehensive coverage for reports; track regulatory changes
- **Pain Points**: Manual source monitoring; inconsistent coverage
- **Usage**: Daily digest with category filters; export for reports

### Persona 3: Portfolio Manager

- **Name**: David
- **Role**: DeFi portfolio manager
- **Goals**: Monitor protocol updates; track governance proposals
- **Pain Points**: Misses critical updates buried in Discord/forums
- **Usage**: Protocol-specific feeds with alerts for high-priority items

---

## User Stories

### US-1: Breaking News Scan (Critical)

**As a** day trader
**I want to** scan for breaking crypto news from the past hour
**So that** I can identify market-moving events before they're priced in

**Acceptance Criteria:**

- Fetch news from past 1h/4h/24h windows
- Display source, title, timestamp, relevance score
- Highlight market-moving keywords (listing, delisting, hack, exploit)
- Complete scan in under 10 seconds

### US-2: Coin-Specific News (Critical)

**As a** researcher
**I want to** filter news for specific coins or tokens
**So that** I can focus on assets in my coverage universe

**Acceptance Criteria:**

- Filter by single coin (--coin BTC) or multiple (--coins BTC,ETH,SOL)
- Match against title, body, and tags
- Include protocol-specific sources (e.g., Solana newsletters for SOL)
- Return results sorted by relevance or recency

### US-3: Category Filtering (Important)

**As a** portfolio manager
**I want to** filter news by category (regulatory, DeFi, NFT, etc.)
**So that** I can focus on my domain without irrelevant noise

**Acceptance Criteria:**

- Categories: regulatory, defi, nft, layer1, layer2, exchange, security
- Multiple categories can be combined
- Category detected via keyword matching and source classification

### US-4: Export to Multiple Formats (Important)

**As a** analyst
**I want to** export news to JSON/CSV
**So that** I can integrate with my research tools and create reports

**Acceptance Criteria:**

- Support table, JSON, CSV output formats
- Include all metadata (source, timestamp, category, relevance)
- Export to file with --output flag

### US-5: Source Management (Nice-to-Have)

**As a** user
**I want to** manage which sources are included in my feed
**So that** I can customize quality and focus

**Acceptance Criteria:**

- List available sources with categories
- Enable/disable specific sources
- Save source preferences to config

---

## Functional Requirements

### REQ-1: Multi-Source Aggregation

- Fetch from RSS feeds (CoinDesk, CoinTelegraph, Decrypt, The Block, etc.)
- Parse feed entries with proper date handling
- Deduplicate across sources based on title similarity

### REQ-2: Relevance Scoring

- Score articles based on keyword matches
- Boost scores for market-moving terms (exploit, hack, listing, partnership)
- Penalize promotional/sponsored content

### REQ-3: Filtering System

- Time-based filtering (1h, 4h, 24h, 7d)
- Coin/token filtering with symbol matching
- Category filtering with multi-select
- Source filtering

### REQ-4: Output Formatting

- Table format for terminal display
- JSON format for programmatic use
- CSV format for spreadsheet analysis
- Minimal format for quick scanning

### REQ-5: Caching

- Cache feed responses to reduce API calls
- Configurable TTL (default 5 minutes)
- Cache invalidation on demand

---

## Non-Goals

- **Social Media Scraping**: No Twitter/Discord/Telegram scraping (API access required, separate skill)
- **Sentiment Analysis**: Basic keyword detection only (sentiment-analyzer is separate skill)
- **Alerts/Notifications**: No push notifications (separate alerting system)
- **Historical Archive**: No long-term storage (scan only, not archive)
- **Translation**: No multi-language support (English sources only)

---

## Success Metrics

| Metric             | Target                        | Measurement           |
| ------------------ | ----------------------------- | --------------------- |
| News fetch time    | < 10s for 50 sources          | Script execution time |
| Source coverage    | 50+ curated sources           | Count in config       |
| Relevance accuracy | > 80% relevant in top 10      | Manual review         |
| User activation    | Triggered by relevant phrases | Plugin analytics      |
| Export success     | 100% valid JSON/CSV           | Format validation     |

---

## UX Flow

```
User: "get latest crypto news"
  │
  ├─► Parse intent (default: 24h, all categories)
  │
  ├─► Fetch from RSS sources (parallel)
  │
  ├─► Parse and normalize entries
  │
  ├─► Score relevance
  │
  ├─► Apply filters (time, category, coin)
  │
  ├─► Sort by relevance or recency
  │
  ├─► Format output (table/JSON/CSV)
  │
  └─► Display or export
```

---

## Integration Points

### Dependencies

- **None** (standalone skill, no other skills required)

### Consumers (Skills that can use this)

- **market-sentiment-analyzer**: Can consume news feed for sentiment analysis
- **crypto-signal-generator**: Can use news as signal input
- **whale-alert-monitor**: Can correlate whale moves with news

### External APIs

- RSS feeds (no API key required)
- CryptoCompare News API (optional, for enhanced coverage)

---

## Constraints & Assumptions

### Constraints

- RSS feed availability (some sources may block or change URLs)
- Rate limiting on news APIs
- No real-time push (polling model only)

### Assumptions

- User has internet connectivity
- English language sources are sufficient
- 5-minute cache TTL is acceptable for most use cases

---

## Risk Assessment

| Risk                 | Likelihood | Impact | Mitigation                                 |
| -------------------- | ---------- | ------ | ------------------------------------------ |
| RSS feed URL changes | Medium     | Medium | Maintain source registry; auto-detection   |
| Feed parsing errors  | Medium     | Low    | Graceful degradation; skip malformed feeds |
| Network timeouts     | Low        | Low    | Timeout per source; parallel fetching      |
| Duplicate articles   | Medium     | Low    | Title-based deduplication                  |

---

## Examples

### Example 1: Default News Scan

```bash
python news_aggregator.py
```

Returns top 20 news items from past 24h, sorted by relevance.

### Example 2: Bitcoin-Specific News

```bash
python news_aggregator.py --coin BTC --period 4h
```

Returns Bitcoin news from past 4 hours.

### Example 3: DeFi Category with Export

```bash
python news_aggregator.py --category defi --format json --output defi_news.json
```

Exports DeFi news to JSON file.

---

## Version History

| Version | Date       | Author           | Changes                  |
| ------- | ---------- | ---------------- | ------------------------ |
| 1.0.0   | 2025-10-16 | Jeremy Longshore | Initial stub             |
| 2.0.0   | 2026-01-14 | Jeremy Longshore | Full PRD, implementation |
