---
name: excel-lbo-modeler
description: 'Build leveraged buyout (LBO) models in Excel with debt schedules and
  IRR analysis.

  Use when structuring LBO transactions or analyzing PE returns.

  Trigger with phrases like ''excel lbo'', ''build lbo model'', ''calculate pe returns''.

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(cmd:*)
version: 1.22.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- business
- excel-lbo
compatibility: Designed for Claude Code
---
# Excel LBO Modeler

## Overview

Creates leveraged buyout models with debt structuring, amortization schedules, and sponsor returns analysis for private equity transactions.

## Prerequisites

- Excel or compatible spreadsheet software
- Target company financial data
- Debt term sheet parameters
- Entry/exit multiple assumptions

## Instructions

1. Set up transaction structure (purchase price, debt/equity split)
2. Build debt schedules for each tranche (senior, mezzanine, etc.)
3. Create operating projections with debt service
4. Calculate cash flow available for debt paydown
5. Model exit scenarios and calculate IRR/MOIC

## Output

- Complete LBO model with sources & uses, debt schedules, and returns
- IRR and MOIC at various exit multiples and years
- Sensitivity tables for entry/exit multiple and leverage

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Negative cash flow | Debt service exceeds EBITDA | Reduce leverage or restructure debt terms |
| IRR #NUM! | No valid solution | Check exit value exceeds equity contribution |
| Circular reference | Cash sweep tied to interest | Enable iterative calculation |

## Examples

**Example: Mid-Market LBO**
Request: "Build an LBO model for a $100M EBITDA company at 8x entry"
Result: 60% senior / 40% equity structure, 5-year model, IRR analysis at 7x-10x exits

**Example: Add-On Acquisition**
Request: "Model a bolt-on acquisition with synergies"
Result: Integrated model with synergy phase-in and accretion analysis

## Resources

- [Macabacus LBO Modeling](https://macabacus.com/)
- [WSO PE Interview Prep](https://www.wallstreetoasis.com/)
- [`references/lbo-formulas.md`](references/lbo-formulas.md) for debt schedule templates
