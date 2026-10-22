---
name: calculating-crypto-taxes
description: 'Calculate cryptocurrency tax obligations with cost basis tracking, capital
  gains computation, and Form 8949 generation.

  Use when calculating crypto taxes, generating tax reports, comparing cost basis
  methods, or identifying taxable events.

  Trigger with phrases like "calculate crypto taxes", "generate tax report", "cost
  basis FIFO", "capital gains", "Form 8949", or "crypto taxable events".

  '
allowed-tools: Read, Write, Bash(crypto:tax-*)
version: 1.28.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- cost-optimization
- calculating-crypto
compatibility: Designed for Claude Code
---
# Calculating Crypto Taxes

## Overview

Calculate cryptocurrency tax obligations from transaction history. Supports FIFO, LIFO, and HIFO cost basis methods, identifies taxable events (trades, staking, airdrops), and generates Form 8949 compatible reports.

**DISCLAIMER**: This tool provides informational calculations only, not tax advice. Consult a qualified tax professional.

## Prerequisites

- Transaction history exported as CSV from your exchanges (Coinbase, Binance, Kraken, etc.)
- Python 3.8+ installed
- Understanding of your tax jurisdiction's crypto rules

## Instructions

1. **Prepare transaction data** by exporting CSV from each exchange:

   | Exchange | Export Location |
   |----------|-----------------|
   | Coinbase | Reports > Tax documents > Transaction history CSV |
   | Binance | Orders > Trade History > Export |
   | Kraken | History > Export |
   | Generic | See [`references/exchange_formats.md`](references/exchange_formats.md) for column mapping |

2. **Run basic tax calculation** using FIFO (IRS default):

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/tax_calculator.py --transactions your_trades.csv --year 2025  # 2025 = tax year
   ```

3. **Compare cost basis methods** to understand tax implications:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/tax_calculator.py --transactions trades.csv --compare-methods
   ```

   Methods: `--method fifo` (IRS default), `--method lifo` (Last In First Out), `--method hifo` (minimize gains)

4. **Generate Form 8949 report** as CSV:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/tax_calculator.py --transactions trades.csv --method fifo --year 2025 --output form_8949.csv --format csv  # 2025 = tax year
   ```

5. **Handle income events** (staking, airdrops, mining, DeFi yield):

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/tax_calculator.py --transactions all_events.csv --income-report
   ```

6. **Consolidate multi-exchange data** into a unified report:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/tax_calculator.py --transactions coinbase.csv binance.csv kraken.csv --year 2025  # 2025 = tax year
   ```

## Output

Reports include short-term and long-term capital gains/losses broken down by transaction, with proceeds, cost basis, and gain/loss per disposal. Summary shows total proceeds, total cost basis, net capital gain, and short/long-term split. Income report lists staking, airdrop, and mining income with fair market values.

See [`references/implementation.md`](references/implementation.md) for detailed output format examples.

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| Missing columns | CSV format mismatch | Verify format matches exchange template |
| Unknown transaction type | Unrecognized event category | Review and manually categorize |
| Insufficient lots | Missing buy transactions | Check for missing imports or transfers |

## Examples

**Basic FIFO tax calculation** - Standard IRS-default method for a single exchange:

```bash
python tax_calculator.py --transactions trades.csv --year 2025  # 2025 = tax year
```

**HIFO to minimize gains** - Highest-cost lots disposed first to reduce taxable gain:

```bash
python tax_calculator.py --transactions trades.csv --method hifo --year 2025  # 2025 = tax year
```

**JSON output for processing** - Machine-readable export for tax software integration:

```bash
python tax_calculator.py --transactions trades.csv --format json --output tax_data.json
```

**Verbose with lot details** - See which specific lots were matched to each disposal:

```bash
python tax_calculator.py --transactions trades.csv --verbose --show-lots
```

## Resources

- IRS Virtual Currency Guidance: https://www.irs.gov/businesses/small-businesses-self-employed/virtual-currencies
- Form 8949 Instructions: https://www.irs.gov/instructions/i8949
- CoinGecko API for historical prices
- [`references/implementation.md`](references/implementation.md) - Detailed output formats, configuration, advanced usage
