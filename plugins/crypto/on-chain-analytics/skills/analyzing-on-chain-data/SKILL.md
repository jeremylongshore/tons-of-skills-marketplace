---
name: analyzing-on-chain-data
description: 'Process perform on-chain analysis including whale tracking, token flows,
  and network activity.

  Use when performing crypto analysis.

  Trigger with phrases like "analyze crypto", "check blockchain", or "monitor market".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(crypto:onchain-*)
version: 1.29.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- monitoring
- analyzing-on
compatibility: Designed for Claude Code
---
# Analyzing On-Chain Data

## Overview

Analyze DeFi protocol metrics, chain-level TVL, fee revenue, DEX volumes, yield opportunities, and stablecoin market caps using DeFiLlama as the primary data source. Designed for DeFi researchers, protocol analysts, and yield farmers who need programmatic access to on-chain analytics without writing custom subgraph queries.

## Prerequisites

- Python 3.8+ with `requests` library installed
- DeFiLlama API access (free, no key required for most endpoints)
- Optional: CoinGecko API key for supplementary token price data
- `onchain_analytics.py` CLI script available in the plugin directory
- `data_fetcher.py` and `metrics_calculator.py` modules for programmatic usage

## Instructions

1. Run `python onchain_analytics.py protocols` to retrieve the top DeFi protocols ranked by total value locked (TVL).
2. Filter protocol results by category using `--category lending`, `--category dex`, or `--category "liquid staking"` to narrow the scope.
3. Filter by chain with `--chain ethereum` or `--chain arbitrum` to isolate chain-specific protocol data.
4. Sort results by alternative metrics using `--sort market_share` or `--sort tvl_to_mcap` to surface undervalued protocols.
5. Run `python onchain_analytics.py chains` to retrieve chain-level TVL rankings across all tracked networks.
6. Run `python onchain_analytics.py fees --protocol aave` to pull fee and revenue data for a specific protocol.
7. Run `python onchain_analytics.py dex --chain ethereum` to analyze DEX trading volumes filtered by chain.
8. Run `python onchain_analytics.py yields --min-tvl 5000000 --chain ethereum` to identify yield opportunities above a minimum TVL threshold.
9. Run `python onchain_analytics.py trends --threshold 5` to detect protocols with significant TVL changes (threshold is percentage).
10. Export results in JSON or CSV format using `--format json` or `--format csv` and redirect to file for downstream analysis.

See [`references/implementation.md`](references/implementation.md) for the full four-step implementation workflow.

## Output

- Protocol rankings table with name, TVL, market share percentage, and TVL-to-market-cap ratio
- Chain TVL rankings showing aggregate locked value per network
- Fee and revenue reports per protocol with daily/weekly/monthly breakdowns
- DEX volume tables with per-chain and per-DEX breakdowns
- Yield opportunity listings filtered by minimum TVL and chain, including APY and pool details
- Trending protocol alerts showing TVL percentage changes above the configured threshold
- Stablecoin market cap summaries
- JSON (`output.json`) or CSV (`output.csv`) export files for programmatic consumption

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Request timeout` | DeFiLlama API slow or unreachable | Wait and retry; check  for outages; use cached data if available |
| `Protocol not found: invalid-name` | Protocol slug does not match DeFiLlama database | Run `python onchain_analytics.py protocols` to find the exact slug; slugs are case-sensitive |
| `No data returned for query` | Filter too restrictive or data unavailable | Remove filters and retry; verify the category or chain exists; try a broader time range |
| `TVL data unavailable for some protocols` | New protocols or data collection gaps | Check DeFiLlama directly; data typically appears within 24 hours of listing |
| `Data may be stale (last updated: X hours ago)` | Local cache not refreshed | Clear cache with `rm ~/.onchain_analytics_cache.json`; use `--verbose` to check cache status |
| `Showing top 50 of 1000+ protocols` | Output truncated for readability | Use `--limit` to increase count or `--format json` for full untruncated data |
| `UnicodeEncodeError` | Terminal encoding mismatch | Use `--format json` for safe output or set `LANG=en_US.UTF-8` |

## Examples

### Daily DeFi Overview

```bash
python onchain_analytics.py protocols --limit 20
python onchain_analytics.py chains
python onchain_analytics.py trends
```

Produces a snapshot of the top 20 protocols by TVL, all chain rankings, and any protocols trending above the default threshold.

### Research a Lending Protocol

```bash
python onchain_analytics.py protocols --category lending --sort tvl_to_mcap
python onchain_analytics.py fees --protocol aave
```

Ranks all lending protocols by TVL-to-market-cap ratio (identifying potentially undervalued protocols), then pulls detailed fee and revenue data for Aave.

### Find High-TVL Yield Opportunities on Ethereum

```bash
python onchain_analytics.py yields --min-tvl 10000000 --chain ethereum --limit 50  # 10000000 = 10M limit
```

Returns up to 50 yield pools on Ethereum with at least $10M in TVL, sorted by APY. Export with `--format csv > yields.csv` for spreadsheet analysis.

## Resources

- [DeFiLlama API Documentation](https://defillama.com/docs/api) -- primary data source for TVL, fees, yields, and DEX volumes
- DeFiLlama Status Page -- check API availability and outage reports
- [CoinGecko API](https://www.coingecko.com/en/api/documentation) -- supplementary token price and market cap data
- [Dune Analytics](https://dune.com/) -- custom SQL queries against on-chain data for deeper analysis
- [The Graph](https://thegraph.com/) -- decentralized indexing protocol for querying blockchain data via GraphQL
