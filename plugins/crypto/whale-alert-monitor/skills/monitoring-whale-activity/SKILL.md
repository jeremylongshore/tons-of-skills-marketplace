---
name: monitoring-whale-activity
description: 'Track large cryptocurrency transactions and whale wallet movements in
  real-time.

  Use when tracking large holder movements, exchange flows, or wallet activity.

  Trigger with phrases like "track whales", "monitor large transfers", "check whale
  activity", "exchange inflows", or "watch wallet".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(python:*whale*)
version: 1.27.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- monitoring
- monitoring-whale
compatibility: Designed for Claude Code
---
# Monitoring Whale Activity

## Contents

[Overview](#overview) | [Prerequisites](#prerequisites) | [Instructions](#instructions) | [Output](#output) | [Error Handling](#error-handling) | [Examples](#examples) | [Resources](#resources)

## Overview

Track large cryptocurrency transactions and whale wallet movements across multiple blockchains. Monitor exchange inflows/outflows, manage custom watchlists, and identify known wallets (exchanges, funds, bridges).

## Prerequisites

1. Install Python 3.8+ with requests library
2. Optionally obtain Whale Alert API key (free tier available for live data)
3. Verify internet access for API calls

## Instructions

### Step 1: Navigate to Scripts Directory

```bash
cd ${CLAUDE_SKILL_DIR}/scripts
```

### Step 2: Choose a Command

1. View recent whale transactions: `python whale_monitor.py recent`
2. Analyze exchange flows: `python whale_monitor.py flows`
3. Manage watchlist: `python whale_monitor.py watchlist`
4. Track specific wallet: `python whale_monitor.py track 0x123...`
5. Search known labels: `python whale_monitor.py labels --query binance`

Alternatively, customize with chain and threshold filters:

```bash
python whale_monitor.py recent --chain ethereum              # Specific chain
python whale_monitor.py recent --min-value 10000000          # 10000000: $10M+ only
python whale_monitor.py watch 0x123... --name "My Whale"     # Add to watchlist
python whale_monitor.py labels --type exchange               # Or use type filter
```

### Step 3: Interpret Results

**Transaction Types:**

- DEPOSIT: Sent to exchange (potential selling pressure)
- WITHDRAWAL: From exchange (accumulation signal)
- TRANSFER: Wallet to wallet (whale movement)

**Flow Analysis:**

- Net positive flow to exchanges = selling pressure
- Net negative flow from exchanges = buying pressure

## Output

- Real-time whale transactions with USD values
- Labeled wallets (exchanges, funds, bridges, protocols)
- Exchange inflow/outflow summaries
- Custom watchlist tracking
- JSON, table, or alert format output (`--format json`)

## Error Handling

See [`references/errors.md`](references/errors.md) for:

- API rate limit handling and backoff
- Network timeout recovery
- Invalid address format validation
- Price service fallbacks

## Examples

**Example 1: View $10M+ whale transactions on Ethereum:**

```bash
python whale_monitor.py recent --chain ethereum --min-value 10000000  # 10000000 = 10M limit
```

**Example 2: Analyze if whales are selling:**

```bash
python whale_monitor.py flows --chain ethereum
```

**Example 3: Track a known whale wallet:**

```bash
python whale_monitor.py watch 0x28c6c... --name "Binance Cold"
python whale_monitor.py track 0x28c6c...
```

**Example 4: Export to JSON for further analysis:**

```bash
python whale_monitor.py recent --format json > whales.json
```

See [`references/examples.md`](references/examples.md) for more usage patterns.

## Resources

- [`references/implementation.md`](references/implementation.md) - Flow analysis, wallet database, multi-chain details
- [Whale Alert](https://whale-alert.io) - Real-time whale transaction API
- [Etherscan](https://etherscan.io) - Ethereum blockchain explorer
- [CoinGecko](https://coingecko.com) - Price data API
