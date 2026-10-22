---
name: excel-dcf-modeler
description: 'Build discounted cash flow (DCF) valuation models in Excel. Use when
  creating

  DCF models, calculating enterprise value, or valuing companies.

  Trigger with phrases like ''excel dcf'', ''build dcf model'', ''calculate enterprise
  value''.

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(cmd:*)
version: 1.22.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- business
- excel-dcf
compatibility: Designed for Claude Code
---
# Excel DCF Modeler

## Overview

Creates professional DCF valuation models following investment banking standards with WACC calculations and sensitivity analysis.

## Prerequisites

- Excel or compatible spreadsheet software
- Historical financial data for target company
- Industry comparables for WACC estimation

## Instructions

1. Create assumptions sheet with revenue growth, margins, WACC, and terminal growth rate
2. Build free cash flow projections (5-year forecast)
3. Calculate terminal value using Gordon Growth Model
4. Discount cash flows and terminal value to present value
5. Sum to get enterprise value, subtract net debt for equity value
6. Add sensitivity tables for key assumptions

## Output

- Complete 4-sheet DCF model with assumptions, projections, valuation, and sensitivity
- Enterprise value and equity value per share
- Sensitivity analysis on WACC and terminal growth rate

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| #DIV/0! in terminal value | WACC equals terminal growth | Terminal growth must be less than WACC |
| Negative FCF | High CapEx or WC needs | Review assumptions, may need different model |
| Unrealistic EV | Extreme growth assumptions | Benchmark against industry comparables |

## Examples

**Example: Value a SaaS Company**
Request: "Create a DCF model for a $50M ARR SaaS company growing 30%"
Result: 4-sheet model with 5-year projections, 12% WACC, 3% terminal growth, sensitivity tables

**Example: M&A Valuation**
Request: "DCF analysis for acquisition target"
Result: Model with synergy adjustments, scenario analysis, and per-share valuation

## Resources

- [Damodaran Online DCF Resources](https://pages.stern.nyu.edu/~adamodar/)
- [WSO DCF Modeling Guide](https://www.wallstreetoasis.com/)
- [`references/dcf-formulas.md`](references/dcf-formulas.md) for Excel formula templates
