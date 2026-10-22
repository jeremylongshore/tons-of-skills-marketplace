---
name: excel-variance-analyzer
description: 'Analyze budget vs actual variances in Excel with drill-down and root
  cause analysis.

  Use when performing variance analysis or explaining budget differences.

  Trigger with phrases like ''excel variance'', ''analyze budget variance'', ''actual
  vs budget''.

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(cmd:*)
version: 1.22.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- business
- excel-variance
compatibility: Designed for Claude Code
---
# Excel Variance Analyzer

## Overview

Performs comprehensive budget vs actual variance analysis with automated drill-down, root cause identification, and executive reporting.

## Prerequisites

- Excel or compatible spreadsheet software
- Budget data by period and category
- Actual results for comparison
- Cost center or department structure

## Instructions

1. Import budget and actual data into comparison template
2. Calculate absolute and percentage variances
3. Apply materiality thresholds for flagging
4. Create drill-down by category, period, or cost center
5. Generate variance waterfall chart for executive reporting

## Output

- Variance summary with favorable/unfavorable indicators
- Materiality-filtered exception report
- Waterfall chart showing budget-to-actual bridge
- Drill-down by category or cost center

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Missing periods | Data gaps | Fill with zeros or interpolate |
| Percentage calc error | Zero budget | Use IF to handle div/0 |
| Misaligned categories | Changed chart of accounts | Create mapping table |

## Examples

**Example: Monthly P&L Variance**
Request: "Analyze why we missed budget by $500K this month"
Result: Variance waterfall showing revenue shortfall offset by OPEX savings

**Example: Department Budget Review**
Request: "Which departments are over budget YTD?"
Result: Ranked list by variance magnitude with drill-down to line items

## Resources

- [FP&A Best Practices](https://www.fpanda.org/)
- [`references/variance-formulas.md`](references/variance-formulas.md) for calculation templates
