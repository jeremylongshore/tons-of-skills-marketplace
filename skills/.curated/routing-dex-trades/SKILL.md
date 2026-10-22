---
name: routing-dex-trades
description: 'Route trades across multiple DEXs to find optimal prices with minimal
  slippage and gas costs.

  Use when comparing DEX prices, finding optimal swap routes, analyzing price impact,
  splitting large orders, or assessing MEV risk.

  Trigger with phrases like "find best swap", "compare DEX prices", "route trade",
  "optimal swap route", "split order", "DEX aggregator", "check slippage", or "MEV
  protection".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(crypto:dex-*)
version: 1.26.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- cost-optimization
- routing-dex
compatibility: Designed for Claude Code
---
# Routing DEX Trades

## Contents

[Overview](#overview) | [Prerequisites](#prerequisites) | [Instructions](#instructions) | [Output](#output) | [Error Handling](#error-handling) | [Examples](#examples) | [Resources](#resources)

## Overview

Optimal trade routing across decentralized exchanges by aggregating quotes from 1inch, Paraswap, and 0x. Discovers multi-hop routes, calculates split orders for large trades, and assesses MEV risk to minimize slippage and gas costs.

## Prerequisites

1. Install Python 3.9+ with `httpx`, `pydantic`, and `rich` packages
2. Verify network access to aggregator APIs (1inch, Paraswap, 0x)
3. Optionally add API keys for 1inch and 0x (higher rate limits)
4. Copy settings: `cp ${CLAUDE_SKILL_DIR}/config/settings.yaml.example ${CLAUDE_SKILL_DIR}/config/settings.yaml`

## Instructions

1. Get a quick quote for the single best price with gas cost and effective rate:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/dex_router.py ETH USDC 1.0
   ```

2. Compare all DEXs to see quotes ranked by effective rate (after gas):

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/dex_router.py ETH USDC 5.0 --compare
   ```

3. Analyze multi-hop routes to compare direct vs. multi-hop (2-3 pools) with hop-by-hop breakdown:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/dex_router.py ETH USDC 10.0 --routes
   ```

4. Split large orders ($10K+) across multiple DEXs to minimize total price impact:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/dex_router.py ETH USDC 100.0 --split
   ```

5. Assess MEV risk (sandwich attack risk score: LOW/MEDIUM/HIGH) before executing:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/dex_router.py ETH USDC 50.0 --mev-check
   ```

6. Run full analysis combining all features for comprehensive output:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/dex_router.py ETH USDC 25.0 --full --output json
   ```

## Output

- **Quick Quote**: Best price, output amount, gas cost, recommended venue
- **Comparison**: All venues ranked by effective rate with price impact and gas
- **Route Analysis**: Direct vs. multi-hop with hop-by-hop breakdown
- **Split Mode**: Optimal allocation percentages with dollar savings vs. single-venue
- **MEV Assessment**: Risk score, exposure estimate, protection recommendations

See [`references/implementation.md`](references/implementation.md) for detailed output examples.

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| API Rate Limited | Too many requests | Wait 60s or add API key for higher limits |
| Quote Expired | Stale price data | Refresh before execution; quotes valid ~30s |
| No Route Found | Low liquidity token | Try larger DEXs or reduce trade size |
| Network Timeout | Aggregator down | Retry or check aggregator status page |

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

**Compare prices for a 5 ETH swap:**

```bash
python ${CLAUDE_SKILL_DIR}/scripts/dex_router.py ETH USDC 5.0 --compare
```

**Find optimal split for a large order:**

```bash
python ${CLAUDE_SKILL_DIR}/scripts/dex_router.py ETH USDC 100.0 --split
```

**Check MEV risk before executing:**

```bash
python ${CLAUDE_SKILL_DIR}/scripts/dex_router.py ETH USDC 50.0 --mev-check
```

See [`references/examples.md`](references/examples.md) for multi-hop discovery and MEV-protected execution examples.

## Resources

- [`references/implementation.md`](references/implementation.md) - Trade size guide, split optimization, MEV scoring, API config
- [1inch API](https://docs.1inch.io/) - Primary aggregator
- [Paraswap API](https://developers.paraswap.network/) - Secondary aggregator
- [0x API](https://0x.org/docs/api) - Third aggregator
- [Flashbots Protect](https://docs.flashbots.net/flashbots-protect/overview) - MEV protection
