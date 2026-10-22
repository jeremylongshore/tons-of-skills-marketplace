---
name: exploring-blockchain-data
description: 'Process query and analyze blockchain data including blocks, transactions,
  and smart contracts.

  Use when querying blockchain data and transactions.

  Trigger with phrases like "explore blockchain", "query transactions", or "check
  on-chain data".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(crypto:explorer-*)
version: 1.31.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- exploring-blockchain
compatibility: Designed for Claude Code
---
# Exploring Blockchain Data

## Overview

Query and analyze blockchain data across multiple EVM-compatible networks including Ethereum, Polygon, Arbitrum, Optimism, and BSC. Supports transaction lookups, address balance checks, block inspection, token balance queries, transaction history retrieval, and whale wallet tracking via a unified CLI.

## Prerequisites

- Python 3.8+ with `requests` and `web3` libraries installed (`pip install requests web3`)
- Etherscan API key (free tier provides 5 requests/second; set via `ETHERSCAN_API_KEY` environment variable)
- Optional: API keys for Polygonscan, Arbiscan, and other chain-specific explorers for higher rate limits
- `blockchain_explorer.py` CLI script, `chain_client.py`, and `token_resolver.py` modules available in the plugin directory
- RPC endpoint access (public endpoints work; dedicated providers like Alchemy, Infura, Chainstack, or QuickNode recommended for reliability)

## Instructions

1. Set the Etherscan API key as an environment variable: `export ETHERSCAN_API_KEY=<key>` to unlock higher rate limits beyond the default 5 requests/second.
2. Run `python blockchain_explorer.py tx <hash>` to look up a transaction by hash, returning status, block number, from/to addresses, value transferred, and gas details.
3. Append `--detailed` to the transaction query to decode the function call, identify the interacting protocol, and display input parameters.
4. Specify `--chain polygon`, `--chain arbitrum`, or `--chain bsc` to query transactions on alternative EVM chains when the hash is not found on Ethereum.
5. Run `python blockchain_explorer.py address <address>` to check the native token balance and total transaction count for a wallet.
6. Add `--history --limit 50` to the address query to retrieve the most recent 50 transactions with timestamps, values, and counterparties.
7. Add `--tokens` to the address query to list all ERC-20 token holdings with balances, symbols, and USD values via CoinGecko price resolution.
8. Run `python blockchain_explorer.py block latest` to inspect the most recent block, or `python blockchain_explorer.py block <number>` for a specific block.
9. Run `python blockchain_explorer.py token <wallet> <contract>` to check the balance of a specific ERC-20 token at a wallet address, with automatic decimal and symbol resolution.
10. Export any query result in JSON or CSV format using `--format json` or `--format csv` and redirect to a file for downstream processing.
11. Enable verbose mode with `--verbose` to display API request URLs, response times, cache hit/miss status, and rate limit counters for debugging.

See [`references/implementation.md`](references/implementation.md) for the full four-step implementation workflow.

## Output

- Transaction detail tables showing hash, chain, status, block number, from/to addresses, value, gas price (Gwei), gas limit, gas used, and gas cost
- Decoded transaction data with function name, protocol identification, and parsed input parameters (when `--detailed` is used)
- Address summary with native balance, transaction count, and explorer link
- Transaction history tables with timestamp, hash, from/to, value, and direction (in/out)
- Token balance listings with contract address, token name, symbol, raw balance, human-readable balance, and USD value
- Block details with block number, timestamp, transaction count, gas used, and miner/validator
- JSON (`output.json`) or CSV (`transactions.csv`) export files for programmatic consumption

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Transaction not found` | Transaction pending in mempool, wrong chain selected, or invalid hash | Wait and retry for pending transactions; try `--chain polygon`, `--chain arbitrum`, `--chain bsc`; verify hash is 66 characters starting with `0x` |
| `Explorer API error: Max rate limit reached` | Too many requests; no API key or quota exhausted | Wait 1-5 seconds and retry; set `ETHERSCAN_API_KEY` for higher limits; upgrade to paid tier for production use |
| `RPC error: execution timeout` | RPC endpoint overloaded or complex query timed out | Retry with a different RPC endpoint; use a dedicated provider (Alchemy, Infura, QuickNode); simplify the query |
| `Invalid address: 0xinvalid` | Address has wrong length, invalid checksum, or non-hex characters | Verify 42 characters with `0x` prefix; use the checksummed version from a block explorer; convert to lowercase if checksum fails |
| `Contract source code not verified` | Contract source not published on the explorer | Use known function signature databases for decoding; check if the contract is a proxy and look up the implementation address |
| `Token: ??? (Unknown Token)` | Token too new, too obscure, or not tracked by CoinGecko | Check the token contract directly on the explorer; look up on a DEX (Uniswap, SushiSwap); manually specify decimals if known |
| `Price: N/A` | Token not listed on CoinGecko, API rate limited, or very low liquidity | Check the DEX for on-chain price; use an alternative price feed; calculate from LP reserves |
| `ImportError: No module named 'requests'` | Missing Python dependencies | Run `pip install requests web3` to install required packages |

## Examples

### Look Up a Transaction Across Chains

```bash
# Try Ethereum first, then Polygon if not found
python blockchain_explorer.py tx 0x1234...abcdef --chain ethereum
python blockchain_explorer.py tx 0x1234...abcdef --chain polygon
```

Returns a formatted table with transaction status, block number, value transferred, gas details, and a link to the block explorer. Adding `--detailed` decodes the function call (e.g., `swapExactTokensForTokens` on Uniswap).

### Full Wallet Analysis

```bash
python blockchain_explorer.py address 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 --history --tokens --limit 50
```

Produces a wallet summary (ETH balance, total transaction count), the 50 most recent transactions with timestamps and counterparties, and a complete ERC-20 token holdings list with USD values. Useful for whale watching or due diligence on a wallet.

### Check USDC Balance and Export to JSON

```bash
python blockchain_explorer.py token 0xYourWallet 0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48 --format json > usdc_balance.json
```

Resolves the USDC contract, fetches the wallet balance with proper decimal handling (6 decimals for USDC), includes the current USD price, and writes the result to `usdc_balance.json` for integration with dashboards or alerting pipelines.

## Resources

- [Etherscan API Documentation](https://docs.etherscan.io/) -- primary explorer API for Ethereum; free tier available with registration
- [CoinGecko API](https://www.coingecko.com/en/api/documentation) -- token price resolution and metadata lookup
- [web3.py Documentation](https://web3py.readthedocs.io/) -- Python library for direct RPC interaction with EVM chains
- [Alchemy](https://docs.alchemy.com/) / [Infura](https://docs.infura.io/) / [QuickNode](https://www.quicknode.com/docs) -- dedicated RPC providers for reliable node access
- [4byte.directory](https://www.4byte.directory/) -- function signature database for decoding unverified contract interactions
