---
name: optimizing-defi-yields
description: 'Find and compare DeFi yield opportunities across protocols with APY
  calculations, risk assessment, and optimization recommendations.

  Use when searching for yield farming opportunities, comparing DeFi protocols, or
  analyzing APY/APR rates.

  Trigger with phrases like "find DeFi yields", "compare APY", "best yield farming",
  "optimize DeFi returns", "stablecoin yields", or "liquidity pool rates".

  '
allowed-tools: Read, Write, Bash(crypto:yield-*)
version: 1.29.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- optimizing-defi
compatibility: Designed for Claude Code
---
# Optimizing DeFi Yields

## Overview

Find and compare DeFi yield opportunities across protocols. Aggregates data from DeFiLlama and other sources to provide APY/APR comparisons, risk assessments, and optimization recommendations for yield farming strategies.

## Prerequisites

Before using this skill, ensure you have:

- Python 3.8+ installed
- Internet access for API queries
- Understanding of DeFi concepts (APY, APR, TVL, impermanent loss)

## Instructions

1. Search for yield opportunities across all chains or filter by a specific chain:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/yield_optimizer.py --top 20
   python ${CLAUDE_SKILL_DIR}/scripts/yield_optimizer.py --chain ethereum --top 10
   ```

2. Filter by criteria -- minimum TVL (for safety), asset type, or protocol:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/yield_optimizer.py --min-tvl 10000000 --top 15  # 10000000 = 10M limit
   python ${CLAUDE_SKILL_DIR}/scripts/yield_optimizer.py --asset USDC --chain ethereum
   python ${CLAUDE_SKILL_DIR}/scripts/yield_optimizer.py --protocol aave,compound,curve
   ```

3. Apply risk filters -- show only audited protocols or filter by risk level (`--risk low`, `--risk medium`, `--risk high`):

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/yield_optimizer.py --audited-only --min-tvl 1000000  # 1000000 = 1M limit
   python ${CLAUDE_SKILL_DIR}/scripts/yield_optimizer.py --risk low --min-apy 3
   ```

4. Analyze specific opportunities -- get detailed pool breakdown or compare protocols:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/yield_optimizer.py --pool "aave-v3-usdc-ethereum" --detailed
   python ${CLAUDE_SKILL_DIR}/scripts/yield_optimizer.py --compare aave,compound,spark --asset USDC
   ```

5. Export results to JSON or CSV for further analysis:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/yield_optimizer.py --top 50 --format json --output yields.json
   python ${CLAUDE_SKILL_DIR}/scripts/yield_optimizer.py --chain ethereum --format csv --output eth_yields.csv
   ```

## Output

### Yield Summary Table

```
==============================================================================
  DEFI YIELD OPTIMIZER                              2026-01-15 15:30 UTC  # 2026 year
==============================================================================

  TOP YIELD OPPORTUNITIES
------------------------------------------------------------------------------
  Protocol       Pool          Chain      TVL        APY    Risk    Score
  Convex        cvxCRV        Ethereum   $450M    12.5%    Low     9.2
  Aave v3       USDC          Ethereum   $2.1B     4.2%    Low     9.8
  Curve         3pool         Ethereum   $890M     3.8%    Low     9.5
  Compound v3   USDC          Ethereum   $1.5B     3.2%    Low     9.6
  Yearn         yvUSDC        Ethereum   $120M     5.1%    Medium  7.8
------------------------------------------------------------------------------

  APY BREAKDOWN (Top Result)
------------------------------------------------------------------------------
  Base APY:     4.5%
  Reward APY:   8.0% (CRV + CVX)
  Total APY:    12.5%
  IL Risk:      None (single-sided)
==============================================================================
```

### Risk Assessment

```
  RISK ANALYSIS: Convex cvxCRV
------------------------------------------------------------------------------
  Audit Status:    ✓ Audited (Trail of Bits, OpenZeppelin)
  Protocol Age:    3+ years
  TVL:             $450M (stable)
  TVL Trend:       +5% (30d)
  Risk Score:      9.2/10 (Low Risk)

  Risk Factors:
  • Smart contract dependency on Curve
  • CRV/CVX reward token volatility
  • Vote-lock mechanics
==============================================================================
```

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

Common issues:

- **API timeout**: Uses cached data with staleness warning
- **No pools found**: Broaden search criteria
- **Invalid protocol**: Check supported protocols list

## Examples

See [`references/examples.md`](references/examples.md) for detailed usage examples.

### Quick Examples

**Find stablecoin yields**:

```bash
python yield_optimizer.py --asset USDC,USDT,DAI --min-tvl 10000000  # 10000000 = 10M limit
```

**Low-risk opportunities**:

```bash
python yield_optimizer.py --risk low --audited-only --min-apy 2
```

**Multi-chain search**:

```bash
python yield_optimizer.py --chain ethereum,arbitrum,polygon --top 20
```

**Export top yields**:

```bash
python yield_optimizer.py --top 100 --format json --output all_yields.json
```

## Configuration

Settings in `${CLAUDE_SKILL_DIR}/config/settings.yaml`:

- **Default chain**: Primary chain to search
- **Cache TTL**: How long to cache API responses
- **Risk weights**: Customize risk scoring factors
- **Min TVL default**: Default minimum TVL filter

## Resources

- DeFiLlama: https://defillama.com/yields - Yield data source
- DeFi Safety:  - Protocol security scores
- Impermanent Loss Calculator: Understand LP risks
