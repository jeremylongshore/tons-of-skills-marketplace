---
name: simulating-flash-loans
description: 'Simulate flash loan strategies with profitability calculations and risk
  assessment across Aave, dYdX, and Balancer.

  Use when simulating flash loans, analyzing arbitrage profitability, evaluating liquidation
  opportunities, or comparing flash loan providers.

  Trigger with phrases like "simulate flash loan", "flash loan arbitrage", "liquidation
  profit", "compare Aave dYdX", "flash loan strategy", or "DeFi arbitrage simulation".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(crypto:flashloan-*)
version: 1.31.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- simulating-flash
compatibility: Designed for Claude Code
---
# Simulating Flash Loans

## Contents

[Overview](#overview) | [Prerequisites](#prerequisites) | [Instructions](#instructions) | [Output](#output) | [Error Handling](#error-handling) | [Examples](#examples) | [Resources](#resources)

## Overview

Simulate flash loan strategies across Aave V3, dYdX, and Balancer with profitability calculations, gas cost estimation, and risk assessment. Evaluate flash loan opportunities without executing real transactions.

## Prerequisites

1. Install Python 3.9+ with `web3`, `httpx`, and `rich` packages
2. Configure RPC endpoint access (free public RPCs via https://chainlist.org work fine)
3. Optionally add Etherscan API key for better gas estimates
4. Set RPC in `${CLAUDE_SKILL_DIR}/config/settings.yaml` or use `ETH_RPC_URL` env var

## Instructions

1. Simulate a two-DEX arbitrage with automatic fee and gas calculation:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/flash_simulator.py arbitrage ETH USDC 100 \
     --dex-buy uniswap --dex-sell sushiswap
   ```

2. Compare flash loan providers to find the cheapest for your strategy:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/flash_simulator.py arbitrage ETH USDC 100 --compare-providers
   ```

3. Analyze liquidation profitability on lending protocols:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/flash_simulator.py liquidation \
     --protocol aave --health-factor 0.95
   ```

4. Simulate triangular arbitrage with multi-hop circular paths:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/flash_simulator.py triangular \
     ETH USDC WBTC ETH --amount 50
   ```

5. Add risk assessment (MEV competition, execution, protocol, liquidity) to any simulation:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/flash_simulator.py arbitrage ETH USDC 100 --risk-analysis
   ```

6. Run full analysis combining all features:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/flash_simulator.py arbitrage ETH USDC 100 \
     --full --output json > simulation.json
   ```

## Output

- **Quick Mode**: Net profit/loss, provider recommendation, Go/No-Go verdict
- **Breakdown Mode**: Step-by-step transaction flow with individual cost components
- **Comparison Mode**: All providers ranked by net profit with fee differences
- **Risk Analysis**: Competition, execution, protocol, and liquidity scores (0-100) with viability grade (A-F)

See [`references/implementation.md`](references/implementation.md) for detailed output examples and risk scoring methodology.

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| RPC Rate Limit | Too many requests | Switch to backup endpoint or wait |
| Stale Prices | Data older than 30s | Auto-refreshes with warning |
| No Profitable Route | All routes lose after costs | Try different pairs or amounts |
| Insufficient Liquidity | Trade exceeds pool depth | Reduce amount or split across pools |

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

**Basic arbitrage simulation:**

```bash
python ${CLAUDE_SKILL_DIR}/scripts/flash_simulator.py arbitrage ETH USDC 100 \
  --dex-buy uniswap --dex-sell sushiswap
```

**Find cheapest provider:**

```bash
python ${CLAUDE_SKILL_DIR}/scripts/flash_simulator.py arbitrage ETH USDC 100 --compare-providers
```

**Liquidation opportunity scan:**

```bash
python ${CLAUDE_SKILL_DIR}/scripts/flash_simulator.py liquidation --protocol aave --health-factor 0.95
```

See [`references/examples.md`](references/examples.md) for multi-provider comparison and backtesting examples.

## Resources

- [`references/implementation.md`](references/implementation.md) - Provider comparison, strategy details, risk scoring, output modes
- [Aave V3 Flash Loans](https://docs.aave.com/developers/guides/flash-loans)
- dYdX Flash Loans
- Balancer Flash Loans
- [Flashbots Protect](https://docs.flashbots.net/flashbots-protect/overview)
