---
name: tracking-token-launches
description: 'Track new token launches across DEXes with risk analysis and contract
  verification.

  Use when discovering new token launches, monitoring IDOs, or analyzing token contracts.

  Trigger with phrases like "track launches", "find new tokens", "new pairs on uniswap",

  "token risk analysis", or "monitor IDOs".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(python:*launch_tracker*)
version: 1.31.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- monitoring
- tracking-token
compatibility: Designed for Claude Code
---
# Token Launch Tracker

## Overview

Monitor new token launches across decentralized exchanges. Detect PairCreated events from DEX factory contracts, fetch token metadata, and analyze contracts for risk indicators like mint functions, blacklists, proxy patterns, and ownership status.

## Prerequisites

Before using this skill, ensure you have:

- Python 3.8+ with `requests` library
- RPC endpoint access (public endpoints work for basic usage)
- Optional: Etherscan API key for contract verification checks
- Optional: Custom RPC URLs for higher rate limits

## Commands

### recent - Show Recent Launches

```bash
python launch_tracker.py recent --chain ethereum --hours 24
python launch_tracker.py recent --chain base --analyze --limit 20
python launch_tracker.py recent --chain bsc --dex "PancakeSwap V2" -f json
```

Options:

- `--chain, -c`: Chain to scan (ethereum, bsc, arbitrum, base, polygon)
- `--hours, -H`: Hours to look back (default: 24)
- `--dex, -d`: Filter by DEX name
- `--limit, -l`: Maximum results (default: 50)
- `--analyze, -a`: Include token and contract analysis
- `--rpc-url`: Custom RPC URL

### detail - Token Details

```bash
python launch_tracker.py detail --address 0x... --chain ethereum
```

Options:

- `--address, -a`: Token contract address (required)
- `--chain, -c`: Chain (default: ethereum)
- `--pair, -p`: Pair address (optional)
- `--etherscan-key`: API key for verification check

### risk - Risk Analysis

```bash
python launch_tracker.py risk --address 0x... --chain base
```

Analyzes contract for risk indicators:

- Mint function (HIGH risk)
- Proxy contract (MEDIUM risk)
- Not verified (MEDIUM risk)
- Blacklist functionality (MEDIUM risk)
- Active owner (LOW risk)

### summary - Launch Statistics

```bash
python launch_tracker.py summary --hours 24
python launch_tracker.py summary --chains ethereum,base,arbitrum
```

### dexes - List DEXes

```bash
python launch_tracker.py dexes --chain bsc
```

### chains - List Chains

```bash
python launch_tracker.py chains
```

## Instructions

1. **Check recent launches** on a specific chain:

   ```bash
   cd ${CLAUDE_SKILL_DIR}/scripts
   python launch_tracker.py recent --chain ethereum --hours 6
   ```

2. **Get detailed token info** for a specific address:

   ```bash
   python launch_tracker.py detail --address 0x6982508145454ce325ddbe47a25d4ec3d2311933 --chain ethereum
   ```

3. **Analyze token risk** before interaction:

   ```bash
   python launch_tracker.py risk --address 0x... --chain base --etherscan-key YOUR_KEY
   ```

4. **View cross-chain summary**:

   ```bash
   python launch_tracker.py summary --hours 24
   ```

5. **Export to JSON** for programmatic use:

   ```bash
   python launch_tracker.py -f json recent --chain ethereum --analyze > launches.json
   ```

## Supported Chains

| Chain | DEXes | Block Time |
|-------|-------|------------|
| Ethereum | Uniswap V2/V3, SushiSwap | 12s |
| BSC | PancakeSwap V2/V3 | 3s |
| Arbitrum | Uniswap V3, Camelot, SushiSwap | 0.25s |
| Base | Uniswap V3, Aerodrome | 2s |
| Polygon | Uniswap V3, QuickSwap, SushiSwap | 2s |

## Risk Indicators

| Indicator | Severity | Description |
|-----------|----------|-------------|
| Mint function | HIGH | Contract can mint new tokens |
| Proxy contract | MEDIUM | Implementation can be changed |
| Not verified | MEDIUM | Source code not public |
| Blacklist/whitelist | MEDIUM | Can restrict transfers |
| Active owner | LOW | Ownership not renounced |
| Small bytecode | INFO | Might be minimal/proxy |

## Output

- **Table format**: Formatted ASCII tables with token data
- **JSON format**: Structured data for programmatic use
- **Risk scores**: 0-100 scale (higher = riskier)
- **Links**: Explorer and DEXScreener URLs

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling including:

- RPC connection issues and fallback chain
- Rate limiting and backoff strategies
- Contract analysis edge cases

## Examples

See [`references/examples.md`](references/examples.md) for detailed examples including:

- Finding high-risk tokens
- Multi-chain monitoring scripts
- Python integration

## Resources

- [Uniswap V2 Factory](https://docs.uniswap.org/contracts/v2/reference/smart-contracts/factory)
- PancakeSwap Factory
- [DEXScreener](https://dexscreener.com/) - Real-time pair data
- [Etherscan API](https://docs.etherscan.io/) - Contract verification
