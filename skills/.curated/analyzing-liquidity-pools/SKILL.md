---
name: analyzing-liquidity-pools
description: 'Analyze DEX liquidity pools for TVL, volume, fees, impermanent loss,
  and LP profitability.

  Use when analyzing liquidity pools, calculating impermanent loss, or comparing DEX
  pools.

  Trigger with phrases like "analyze liquidity pool", "calculate impermanent loss",
  "LP returns", "pool TVL", "DEX pool metrics", or "compare pools".

  '
allowed-tools: Read, Write, Bash(crypto:liquidity-*)
version: 1.24.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- analyzing-liquidity
compatibility: Designed for Claude Code
---
# Analyzing Liquidity Pools

## Overview

Analyze DEX liquidity pools across Uniswap, Curve, and Balancer to evaluate TVL, trading volume, fee income, and impermanent loss risk. Compare pools across protocols and chains to identify optimal LP opportunities.

## Prerequisites

- Python 3.8+ installed
- Internet access for subgraph/API queries
- Understanding of liquidity providing concepts (IL, fee tiers, TVL)

## Instructions

1. **Analyze a specific pool** by address or token pair:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/pool_analyzer.py --pool 0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640
   python ${CLAUDE_SKILL_DIR}/scripts/pool_analyzer.py --pair ETH/USDC --protocol uniswap-v3
   ```

2. **Calculate impermanent loss** for a price change:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/pool_analyzer.py --il-calc --entry-price 2000 --current-price 3000  # 2000/3000 = ETH price at entry/now in USD
   ```

   Project IL for various scenarios:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/pool_analyzer.py --il-scenarios --token-pair ETH/USDC
   ```

3. **Estimate LP returns** with fee APR and position projections:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/pool_analyzer.py --pool [address] --detailed
   python ${CLAUDE_SKILL_DIR}/scripts/pool_analyzer.py --pool [address] --position 10000  # 10000 = LP position size in USD
   ```

4. **Compare pools** across protocols or fee tiers:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/pool_analyzer.py --compare --pair ETH/USDC --protocols uniswap-v3,curve,balancer
   python ${CLAUDE_SKILL_DIR}/scripts/pool_analyzer.py --compare --pair ETH/USDC --fee-tiers 0.05,0.30,1.00
   ```

5. **Export results** to JSON or CSV:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/pool_analyzer.py --pool [address] --format json --output pool_analysis.json
   python ${CLAUDE_SKILL_DIR}/scripts/pool_analyzer.py --compare --pair ETH/USDC --format csv --output pools.csv
   ```

## Output

Pool analysis reports include chain, TVL, 24h volume, fee tier, fee APR, volume/TVL ratio, and token composition with current price. Impermanent loss reports show IL percentage, dollar impact, HODL vs LP value comparison, and breakeven analysis with days-to-recover based on fee income.

See [`references/implementation.md`](references/implementation.md) for detailed output format examples.

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| Pool not found | Wrong address or chain | Verify address and target chain |
| Subgraph timeout | API latency or downtime | Uses cached data with warning |
| Invalid pair | Unsupported protocol | Check supported protocols list |

## Examples

**Analyze top ETH/USDC pool** - Full TVL, volume, and fee breakdown on Uniswap V3:

```bash
python pool_analyzer.py --pair ETH/USDC --protocol uniswap-v3 --chain ethereum
```

**Calculate IL for 2x price increase** - See dollar impact vs holding:

```bash
python pool_analyzer.py --il-calc --entry-price 100 --current-price 200  # 100/200 = token price at entry/now in USD
```

**Compare Uniswap fee tiers** - Find optimal fee tier for ETH/USDC:

```bash
python pool_analyzer.py --compare --pair ETH/USDC --fee-tiers 0.05,0.30,1.00
```

**Export all ETH pairs** - Dump pool data for further analysis:

```bash
python pool_analyzer.py --token ETH --format json --output eth_pools.json
```

## Resources

- The Graph: https://thegraph.com/ - Subgraph queries
- Uniswap Info: https://info.uniswap.org/ - Pool explorer
- DeFiLlama: https://defillama.com/ - TVL data
- [`references/implementation.md`](references/implementation.md) - Detailed output formats, configuration, cross-protocol comparison guide
