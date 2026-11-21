---
name: coreweave-gpu-cost-leak-hunter
description: |
  Review CoreWeave GPU usage and cost scenarios from supplied billing and telemetry evidence.
  Use when investigating a high GPU bill, idle reservations, right-sizing or a commitment decision.
  Separate measured usage from estimated spend and billing-backed amounts.
  Trigger with "coreweave cost", "why is my coreweave bill", "idle reserved capacity",
  "GPU cost leak", or "GPU usage and cost review".
allowed-tools: Read, Write, Edit, Glob, Bash(curl:*), Bash(jq:*), Bash(kubectl get:*), Bash(python3:*)
version: 1.15.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, coreweave, gpu-cloud, finops, cost]
metadata:
  display-name: GPU usage and cost review for CoreWeave
---
# GPU usage and cost review for CoreWeave

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Review usage, rates and workload context without claiming telemetry is an invoice or low utilization proves waste.
The stable install identifier remains `coreweave-gpu-cost-leak-hunter`; the public task is a GPU usage and cost review.
CoreWeave provides cost/usage monitoring and an official Mission Control MCP FOCUS usage tool. That tool returns usage quantities, not dollar amounts.
Use Read for the authorized exports, Glob for selected finding files, Write the report and Edit the proposed assumptions after owner review.

## Prerequisites

- An explicit UTC window, cluster/product scope, capacity plan and authorized data source.
- Usage with units, completeness/freshness and pagination receipts; actual customer rates with source/date/currency.
- Workload phase, availability and checkpoint context before classifying an idle-looking interval.
- Python 3 for offline arithmetic; no credential or paid workload is needed for supplied fixture data.
- A billing owner for invoice reconciliation and a workload owner for any capacity change.

## Instructions

1. Start with the official cost/usage guidance and available read-only Mission Control tools. Request the required permissions rather than claiming a missing metric proves a missing role. Empty data, access denial and measured zero are different states.
2. For `coreweave_billing_get_focus_usage`, set explicit start/end timestamps, preserve scope across page tokens, and fetch every page. Record `data_as_of`; a recent incomplete window is not settled billing.
3. Preserve usage units. `billing:instance:total` counts instances, not individual GPUs; converting samples to GPU-hours requires the observed time step, coverage and GPUs per instance. Do not invent a `billing_gpu` recording rule or reservation label.
4. Review the four categories in references: idle reservation exposure, right-sizing scenarios, idle-looking allocation and commitment scenarios. Separate Reserved Instance, Flex holding/usage, Spot and On-Demand terms. Contract obligations may make an apparent exposure unrecoverable.
5. Assemble one reviewed finding object per scenario. Usage times rate defaults to `estimated`; `confirmed` requires a supplied billed amount and an explicit billing evidence reference. This offline script cannot verify that reference itself.
6. Run the ranker. It rejects missing/negative/non-finite amounts, unknown confidence labels and conflicting modifiers. Findings can overlap, so it does not sum them into a savings headline.
7. Have the owners validate the source, assumptions, overlap and proposed experiment. A report does not authorize scaling, cancellation or a new reservation commitment.

## Examples

Illustrative fixture input, not a measured customer result:

```json
[
  {
    "category": "Idle-looking allocation",
    "root_cause": "Utilization review required; checkpointing not yet excluded",
    "fix": "Review with workload and billing owners",
    "kind": "estimated",
    "usage_gpu_hours": 100,
    "rate_usd_per_gpu_hour": 2,
    "evidence": "Synthetic 30-day fixture; rate is illustrative"
  }
]
```

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/rank-and-report.py" \
  --in findings.json --window-end 2026-11-05 --out cost-review.md
python3 "${CLAUDE_SKILL_DIR}/scripts/rank-and-report.py" --self-test
```

The fixture is $200 over its supplied 30-day window; the monthly-equivalent calculation is labeled separately.
A `confirmed` row must additionally supply `waste_30d_usd` and `billing_evidence`, with the billed attribution reviewed by the owner.

## Output

- Findings ranked within separate billing-backed, estimated and contract-dependent sections.
- Explicit window, conversion, evidence/assumption and overlap disclosures.
- A proposed owner review rather than a guaranteed saving, invented invoice or automatic resource change.

## Error Handling

| Condition | Response |
|---|---|
| Missing access, samples or page | Mark incomplete; do not report zero waste. |
| Missing/NaN/infinite/negative number | Reject the report before writing it. |
| Missing confidence | Default to estimated, never confirmed. |
| Claimed confirmed amount without billing reference | Reject; require owner-reviewed billing attribution. |
| Reservation/capacity terms unknown | Keep the scenario at-risk and obtain contract details before financial conclusions. |

## Resources

- [Review categories](references/gpu-cost-leak-categories.md)
- [Report interpretation](references/cfo-output-format.md)
- [Right-sizing evidence](references/gpu-right-sizing.md)
- [Usage access and units](references/promql-billing-setup.md)
- [CoreWeave cost and usage](https://docs.coreweave.com/observability/usage-monitoring)
- [Mission Control tool reference](https://docs.coreweave.com/observability/mission-control-mcp/reference/tools)

## Evidence status

Offline arithmetic and input-validation fixtures pass separately from live data access. No customer billing, utilization, recovered cash, measured savings or provider-backed skill evaluation is established by these fixtures.
