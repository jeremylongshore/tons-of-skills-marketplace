---
name: optimizing-staking-rewards
description: 'Compare and optimize staking rewards across validators, protocols, and
  blockchains with risk assessment.

  Use when analyzing staking opportunities, comparing validators, calculating staking
  rewards, or optimizing PoS yields.

  Trigger with phrases like "optimize staking", "compare staking", "best staking APY",
  "liquid staking", "validator comparison", "staking rewards", or "ETH staking options".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(crypto:staking-*)
version: 1.27.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- optimizing-staking
compatibility: Designed for Claude Code
---
# Optimizing Staking Rewards

## Overview

Analyze staking opportunities across PoS blockchains and liquid staking protocols. Compares APY/APR, calculates net yields after fees, assesses protocol risks, and recommends optimal allocations.

## Prerequisites

1. **Python 3.8+** installed
2. **Dependencies**: `pip install requests`
3. Network access to DeFiLlama APIs
4. Optional: CoinGecko API key for higher rate limits

## Instructions

1. **Compare staking options** for a specific asset:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/staking_optimizer.py --asset ETH
   ```

   Shows protocol name, type (native vs liquid), gross/net APY, risk score, TVL, and lock-up period.

2. **Analyze with position size** for gas-adjusted yields:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/staking_optimizer.py --asset ETH --amount 10
   ```

   Calculates effective APY accounting for gas costs and projects returns at 1M, 3M, 6M, and 1Y.

3. **Optimize existing portfolio** with current positions:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/staking_optimizer.py --optimize \
     --positions "10 ETH @ lido 4.0%, 100 ATOM @ native 18%, 50 DOT @ native 14%"
   ```

   Suggests higher-yield alternatives with projected improvement and switching costs.

4. **Compare protocols or run risk assessment**:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/staking_optimizer.py --compare --protocols lido,rocket-pool,frax-ether
   python ${CLAUDE_SKILL_DIR}/scripts/staking_optimizer.py --asset ETH --detailed
   ```

5. **Export results** in JSON or CSV:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/staking_optimizer.py --asset ETH --format json --output staking.json
   ```

## Output

Comparison table ranked by risk-adjusted return (Net APY multiplied by Risk Score / 10), showing native and liquid staking options:

```
  STAKING OPTIONS FOR ETH                              2025-01-15 15:30 UTC  # 2025 timestamp
  Protocol        Type      Gross APY  Net APY  Risk   TVL         Unbond
  Frax (sfrxETH)  liquid      5.10%     4.59%   7/10   $450M       instant
  Lido (stETH)    liquid      4.00%     3.60%   9/10   $15B        instant
  Rocket Pool     liquid      4.20%     3.61%   8/10   $3B         instant
  Coinbase cbETH  liquid      3.80%     3.42%   9/10   $2B         instant
  ETH Native      native      4.00%     4.00%   10/10  $50B        variable
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| API timeout | DeFiLlama unreachable | Cached data used with warning |
| Invalid asset | Unknown staking asset | Lists supported assets |
| Rate limited | Too many API calls | Automatic retry with backoff |
| No data found | Protocol not indexed | Falls back to known protocol list |

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

Common staking analysis workflows from single-asset comparison to full portfolio optimization:

```bash
# Quick ETH staking comparison
python ${CLAUDE_SKILL_DIR}/scripts/staking_optimizer.py --asset ETH

# Large position with full risk analysis
python ${CLAUDE_SKILL_DIR}/scripts/staking_optimizer.py --asset ETH --amount 100 --detailed

# Multi-asset comparison exported to CSV
python ${CLAUDE_SKILL_DIR}/scripts/staking_optimizer.py --assets ETH,SOL,ATOM --format csv

# Portfolio optimization with current positions
python ${CLAUDE_SKILL_DIR}/scripts/staking_optimizer.py --optimize \
  --positions "50 ETH @ lido 3.6%, 500 SOL @ marinade 7.5%"  # 500 - minimum stake amount in tokens
```

## Resources

- [`references/implementation.md`](references/implementation.md) - Optimization reports, risk assessment details, disclaimers
- [`references/errors.md`](references/errors.md) - Comprehensive error handling
- DeFiLlama Yields: https://defillama.com/yields
- StakingRewards: https://www.stakingrewards.com
- Lido: https://lido.fi | Rocket Pool: https://rocketpool.net
