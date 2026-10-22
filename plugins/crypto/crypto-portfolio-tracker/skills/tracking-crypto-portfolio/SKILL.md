---
name: tracking-crypto-portfolio
description: 'Track cryptocurrency portfolio with real-time valuations, allocation
  analysis, and P&L tracking.

  Use when checking portfolio value, viewing holdings breakdown, analyzing allocations,
  or exporting portfolio data.

  Trigger with phrases like "show my portfolio", "check crypto holdings", "portfolio
  allocation", "track my crypto", or "export portfolio".

  '
allowed-tools: Read, Write, Bash(crypto:portfolio-*)
version: 1.28.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- tracking-crypto
compatibility: Designed for Claude Code
---
# Tracking Crypto Portfolio

## Overview

Track cryptocurrency holdings with real-time CoinGecko valuations, allocation analysis, P&L tracking, and concentration risk alerts.

## Prerequisites

1. **Python 3.8+** installed
2. **Dependencies**: `pip install requests`
3. Internet connectivity for CoinGecko API access
4. A portfolio JSON file with your holdings (see `references/implementation.md` for format)

## Instructions

1. **Assess user intent** - determine what portfolio view is needed:
   - Quick check: total value and top holdings
   - Holdings list: full breakdown of all positions
   - Detailed analysis: allocations, P&L, risk flags
   - Export: JSON or CSV for external tools

2. **Run the portfolio tracker** with appropriate options:

   ```bash
   # Quick portfolio summary
   python ${CLAUDE_SKILL_DIR}/scripts/portfolio_tracker.py --portfolio holdings.json

   # Full holdings breakdown
   python ${CLAUDE_SKILL_DIR}/scripts/portfolio_tracker.py --portfolio holdings.json --holdings

   # Detailed analysis with P&L and allocations
   python ${CLAUDE_SKILL_DIR}/scripts/portfolio_tracker.py --portfolio holdings.json --detailed
   ```

3. **Export results** for analysis tools or tax reporting:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/portfolio_tracker.py --portfolio holdings.json --format json --output portfolio_export.json
   python ${CLAUDE_SKILL_DIR}/scripts/portfolio_tracker.py --portfolio holdings.json --format csv --output portfolio.csv
   ```

4. **Present results** to the user:
   - Show total portfolio value prominently
   - Highlight 24h and 7d changes
   - Explain allocation percentages
   - Flag any concentration risks (positions > 25% allocation by default)

## Output

Summary showing total value, 24h/7d changes, per-asset allocation, and concentration warnings for positions exceeding threshold:

```
==============================================================================
  CRYPTO PORTFOLIO TRACKER                          Updated: 2026-01-14 15:30  # 2026 - current year timestamp
==============================================================================

  PORTFOLIO SUMMARY: My Portfolio
------------------------------------------------------------------------------
  Total Value:    $125,450.00 USD
  24h Change:     +$2,540.50 (+2.07%)
  7d Change:      +$8,125.00 (+6.92%)
  Holdings:       8 assets

  TOP HOLDINGS
------------------------------------------------------------------------------
  Coin     Quantity      Price         Value      Alloc   24h
  BTC      0.500     $95,000.00   $47,500.00    37.9%   +2.5%
  ETH      10.000     $3,200.00   $32,000.00    25.5%   +1.8%
  SOL      100.000      $180.00   $18,000.00    14.4%   +4.2%

  WARNING: BTC (37.9%) exceeds 25% threshold

==============================================================================
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Portfolio file not found | Invalid path | Check file path exists |
| Invalid JSON | Malformed file | Validate JSON syntax |
| Coin not found | Unknown symbol | Check symbol spelling, use standard symbols |
| API rate limited | Too many requests | Wait and retry, use caching |

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

Portfolio tracking workflows from quick checks to detailed analysis and export:

```bash
# Basic portfolio check
python ${CLAUDE_SKILL_DIR}/scripts/portfolio_tracker.py --portfolio ~/crypto/holdings.json

# All holdings sorted by allocation
python ${CLAUDE_SKILL_DIR}/scripts/portfolio_tracker.py --portfolio holdings.json --holdings --sort allocation

# Detailed analysis with custom 15% threshold
python ${CLAUDE_SKILL_DIR}/scripts/portfolio_tracker.py --portfolio holdings.json --detailed --threshold 15

# Export for tax software
python ${CLAUDE_SKILL_DIR}/scripts/portfolio_tracker.py --portfolio holdings.json --format csv --output tax_export.csv
```

## Resources

- [`references/implementation.md`](references/implementation.md) - Portfolio file format, CLI options, allocation thresholds, JSON format
- [`references/errors.md`](references/errors.md) - Comprehensive error handling
- [`references/examples.md`](references/examples.md) - Detailed usage examples
- CoinGecko API: https://www.coingecko.com/en/api
- `${CLAUDE_SKILL_DIR}/config/settings.yaml` - Configuration options
