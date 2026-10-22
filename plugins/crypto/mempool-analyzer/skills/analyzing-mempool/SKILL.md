---
name: analyzing-mempool
description: 'Monitor blockchain mempools for pending transactions, gas analysis,
  and MEV opportunities.

  Use when analyzing pending transactions, optimizing gas prices, or researching MEV.

  Trigger with phrases like "check mempool", "scan pending txs", "find MEV", "gas
  price analysis", or "pending swaps".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(python:*mempool*)
version: 1.33.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- monitoring
- analyzing-mempool
compatibility: Designed for Claude Code
---
# Analyzing Mempool

## Contents

[Overview](#overview) | [Prerequisites](#prerequisites) | [Instructions](#instructions) | [Output](#output) | [Error Handling](#error-handling) | [Examples](#examples) | [Resources](#resources)

## Overview

Monitor Ethereum mempool for pending transactions, analyze gas prices, detect DEX swaps, and identify potential MEV opportunities. Useful for traders, MEV researchers, and protocol developers.

## Prerequisites

1. Install Python 3.8+ with requests library
2. Configure Ethereum RPC URL (default: public endpoint, or set `ETH_RPC_URL`)
3. Verify internet access for RPC calls

## Instructions

### Step 1: Navigate to Scripts Directory

```bash
cd ${CLAUDE_SKILL_DIR}/scripts
```

### Step 2: Choose a Command

1. View pending transactions: `python mempool_analyzer.py pending`
2. Analyze gas prices: `python mempool_analyzer.py gas`
3. Detect pending DEX swaps: `python mempool_analyzer.py swaps`
4. Scan MEV opportunities: `python mempool_analyzer.py mev`
5. Get mempool summary: `python mempool_analyzer.py summary`
6. Watch specific contract: `python mempool_analyzer.py watch 0x7a250d...`

Alternatively, customize with flags:

```bash
python mempool_analyzer.py pending --limit 100    # Limit results
python mempool_analyzer.py --chain polygon gas     # Use different chain
python mempool_analyzer.py --chain arbitrum pending # Or use Arbitrum
```

### Step 3: Interpret Results

**Gas Recommendations:**

- Slow (10th percentile): May take 10+ blocks
- Standard (50th percentile): 2-5 blocks
- Fast (75th percentile): 1-2 blocks
- Instant (90th percentile): Next block likely

**MEV Warnings:**

- MEV detection is for educational purposes
- Real MEV extraction requires specialized infrastructure
- Use this for research and understanding mempool dynamics

## Output

- Pending transaction lists with gas prices and types
- Gas price distribution and recommendations
- Detected DEX swaps with amounts and DEX identification
- MEV opportunity analysis with estimated profits
- JSON output for programmatic use (`--format json`)

## Error Handling

See [`references/errors.md`](references/errors.md) for:

- RPC connection issues and timeout recovery
- Mempool access limitations per chain
- Transaction decoding errors and fallbacks
- Gas analysis edge cases

## Examples

**Example 1: Check gas before sending transaction:**

```bash
python mempool_analyzer.py gas
# Use "Fast" for quick confirmation
```

**Example 2: Monitor for large pending swaps:**

```bash
python mempool_analyzer.py swaps --limit 200  # 200: max results to scan
```

**Example 3: Research MEV opportunities:**

```bash
python mempool_analyzer.py mev -v
```

See [`references/examples.md`](references/examples.md) for more usage patterns.

## Resources

- [`references/implementation.md`](references/implementation.md) - Gas analysis, MEV detection, multi-chain details
- [Ethereum JSON-RPC](https://ethereum.org/en/developers/docs/apis/json-rpc/) - RPC specification
- [Flashbots](https://flashbots.net) - MEV research and infrastructure
- [DEX Subgraphs](https://thegraph.com) - Pool and swap data
- Supports: Ethereum, Polygon, Arbitrum, Optimism, Base
