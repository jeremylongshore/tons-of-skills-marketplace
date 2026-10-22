---
name: monitoring-cross-chain-bridges
description: 'Monitor cross-chain bridge TVL, volume, fees, and transaction status
  across networks.

  Use when researching bridges, comparing routes, or tracking bridge transactions.

  Trigger with phrases like "monitor bridges", "compare bridge fees", "track bridge
  tx",

  "bridge TVL", or "cross-chain transfer status".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(python:*bridge_monitor*)
version: 1.28.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- monitoring
- monitoring-cross
compatibility: Designed for Claude Code
---
# Cross-Chain Bridge Monitor

## Overview

Monitor cross-chain bridge activity across multiple protocols. Track TVL, compare fees and transfer times, and monitor transaction status for bridges like Stargate, Across, Wormhole, and LayerZero.

## Prerequisites

Before using this skill, ensure you have:

- Python 3.8+ with `requests` library
- Internet access for DefiLlama and bridge APIs
- Optional: Custom RPC URLs for on-chain verification

## Commands

### tvl - Bridge TVL Rankings

```bash
python bridge_monitor.py tvl --limit 20
```

Shows bridges ranked by Total Value Locked.

### bridges - List All Bridges

```bash
python bridge_monitor.py bridges
python bridge_monitor.py bridges --chain arbitrum
```

Lists bridges by 24h volume with optional chain filter.

### detail - Bridge Details

```bash
python bridge_monitor.py detail --bridge stargate
```

Shows detailed info including volume, chains, and TVL breakdown.

### compare - Compare Routes

```bash
python bridge_monitor.py compare --source ethereum --dest arbitrum --amount 1000 --token USDC  # 1000: 1 second in ms
```

Compares fees and transfer times across bridges for a route.

### tx - Track Transaction

```bash
python bridge_monitor.py tx --tx-hash 0x...
python bridge_monitor.py tx --tx-hash 0x... --bridge wormhole
```

Tracks bridge transaction status across protocols.

### chains - List Chains

```bash
python bridge_monitor.py chains
```

Shows all supported chains.

### protocols - List Protocols

```bash
python bridge_monitor.py protocols
```

Shows supported bridge protocols with their chains.

## Instructions

1. **Check bridge TVL rankings**:

   ```bash
   cd ${CLAUDE_SKILL_DIR}/scripts
   python bridge_monitor.py tvl
   ```

2. **Compare bridge routes** before transferring:

   ```bash
   python bridge_monitor.py compare -s ethereum -d base -a 5000 -t USDC  # 5000: bridge transfer amount in USD
   ```

3. **Get bridge details** for research:

   ```bash
   python bridge_monitor.py detail --bridge across
   ```

4. **Track a transaction**:

   ```bash
   python bridge_monitor.py tx --tx-hash 0x1234...
   ```

5. **Export to JSON** for analysis:

   ```bash
   python bridge_monitor.py -f json bridges > bridges.json
   ```

## Supported Bridges

| Bridge | Type | Avg Time | Typical Fee |
|--------|------|----------|-------------|
| Wormhole | Messaging | ~15 min | ~0.1% |
| LayerZero | Messaging | ~3 min | ~0.06% |
| Stargate | Liquidity | ~2 min | ~0.06% |
| Across | Liquidity | ~1 min | ~0.04% |

## Supported Chains

- Ethereum, BSC, Polygon, Arbitrum, Optimism
- Base, Avalanche, Fantom, Solana (Wormhole)
- 45+ total chains via DefiLlama

## Output

- **TVL rankings**: Bridges sorted by locked value
- **Fee comparison**: Side-by-side fee and time estimates
- **TX status**: Source/destination confirmation status
- **JSON format**: Structured data with `-f json` flag

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling including:

- API unavailability and fallback behavior
- Transaction tracking edge cases
- Rate limiting mitigation

## Examples

See [`references/examples.md`](references/examples.md) for detailed examples including:

- Finding best route for large transfers
- Monitoring transactions after bridging
- Research workflows for bridge safety

## Resources

- [DefiLlama Bridges](https://defillama.com/bridges) - Bridge TVL and volume
- [Wormhole Scan](https://wormholescan.io/) - Wormhole transaction explorer
- [LayerZero Scan](https://layerzeroscan.com/) - LayerZero message explorer
- [Across Protocol](https://across.to/) - Optimistic bridge
