---
name: analyzing-market-sentiment
description: 'Analyze cryptocurrency market sentiment using Fear & Greed Index, news
  analysis, and market momentum.

  Use when gauging overall market mood, checking if markets are fearful or greedy,
  or analyzing sentiment for specific coins.

  Trigger with phrases like "analyze crypto sentiment", "check market mood", "is the
  market fearful", "sentiment for Bitcoin", or "Fear and Greed index".

  '
allowed-tools: Read, Bash(crypto:sentiment-*)
version: 1.25.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- analyzing-market
compatibility: Designed for Claude Code
---
# Analyzing Market Sentiment

## Overview

Cryptocurrency market sentiment analysis combining Fear & Greed Index, news keyword analysis, and price/volume momentum into a composite 0-100 score.

## Prerequisites

1. **Python 3.8+** installed
2. **Dependencies**: `pip install requests`
3. Internet connectivity for API access (Alternative.me, CoinGecko)
4. Optional: `crypto-news-aggregator` skill for enhanced news analysis

## Instructions

1. **Assess user intent** - determine what analysis is needed:
   - Overall market: no specific coin, general sentiment
   - Coin-specific: extract symbol (BTC, ETH, etc.)
   - Quick vs detailed: quick score or full component breakdown

2. **Run sentiment analysis** with appropriate options:

   ```bash
   # Quick market sentiment check
   python ${CLAUDE_SKILL_DIR}/scripts/sentiment_analyzer.py

   # Coin-specific sentiment
   python ${CLAUDE_SKILL_DIR}/scripts/sentiment_analyzer.py --coin BTC

   # Detailed breakdown with all components
   python ${CLAUDE_SKILL_DIR}/scripts/sentiment_analyzer.py --detailed

   # Custom time period
   python ${CLAUDE_SKILL_DIR}/scripts/sentiment_analyzer.py --period 7d --detailed
   ```

3. **Export results** for trading models or analysis:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/sentiment_analyzer.py --format json --output sentiment.json
   ```

4. **Present results** to the user:
   - Show composite score and classification prominently
   - Explain what the sentiment reading means
   - Highlight extreme readings (potential contrarian signals)
   - For detailed mode, show component breakdown with weights

## Output

Composite sentiment score (0-100) with classification and weighted component breakdown. Extreme readings serve as contrarian indicators:

```
==============================================================================
  MARKET SENTIMENT ANALYZER                         Updated: 2026-01-14 15:30  # 2026 - current year timestamp
==============================================================================

  COMPOSITE SENTIMENT
------------------------------------------------------------------------------
  Score: 65.5 / 100                         Classification: GREED

  Component Breakdown:
  - Fear & Greed Index:  72.0  (weight: 40%)  -> 28.8 pts
  - News Sentiment:      58.5  (weight: 40%)  -> 23.4 pts
  - Market Momentum:     66.5  (weight: 20%)  -> 13.3 pts

  Interpretation: Market is moderately greedy. Consider taking profits or
  reducing position sizes. Watch for reversal signals.

==============================================================================
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Fear & Greed unavailable | API down | Uses cached value with warning |
| News fetch failed | Network issue | Reduces weight of news component |
| Invalid coin | Unknown symbol | Proceeds with market-wide analysis |

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

Sentiment analysis patterns from quick checks to custom-weighted deep analysis:

```bash
# Quick market sentiment
python ${CLAUDE_SKILL_DIR}/scripts/sentiment_analyzer.py

# Bitcoin-specific sentiment
python ${CLAUDE_SKILL_DIR}/scripts/sentiment_analyzer.py --coin BTC

# Detailed analysis with component breakdown
python ${CLAUDE_SKILL_DIR}/scripts/sentiment_analyzer.py --detailed

# Custom weights emphasizing news
python ${CLAUDE_SKILL_DIR}/scripts/sentiment_analyzer.py --weights "news:0.5,fng:0.3,momentum:0.2"

# Weekly sentiment trend
python ${CLAUDE_SKILL_DIR}/scripts/sentiment_analyzer.py --period 7d --detailed
```

## Resources

- [`references/implementation.md`](references/implementation.md) - CLI options, classifications, JSON format, contrarian theory
- [`references/errors.md`](references/errors.md) - Comprehensive error handling
- [`references/examples.md`](references/examples.md) - Detailed usage examples
- Alternative.me Fear & Greed: https://alternative.me/crypto/fear-and-greed-index/
- CoinGecko API: https://www.coingecko.com/en/api
- `${CLAUDE_SKILL_DIR}/config/settings.yaml` - Configuration options
