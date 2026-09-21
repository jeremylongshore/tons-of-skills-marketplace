---
name: castai-cost-tuning
description: 'Analyze CAST AI cost, available-savings, and realized-savings reports into a defensible optimization plan. Use when investigating spend, validating savings claims, applying private-price adjustments, or prioritizing workloads and clusters. Trigger with: "tune CAST AI costs", "verify CAST AI savings", "reduce Kubernetes spend with CAST AI".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[cluster-or-organization-report]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - kubernetes
  - cast-ai
  - finops
  - cost-optimization
compatibility: 'Requires CAST AI Cost Monitoring data and access to the organization pricing and workload context needed to interpret it'
---

# CAST AI Cost Evidence Review

## Overview

Turn reporting into a prioritized plan without treating modeled savings as invoices. Separate actual spend, available opportunity, realized savings, workload rightsizing, adoption, pricing, and baseline assumptions.

## Prerequisites

- The organization and cluster reports for a declared time range
- Cloud billing or internal allocation evidence for reconciliation
- Current automation adoption, workload SLOs, and pricing-adjustment ownership

## Instructions

### Step 1: Normalize the question

Use Read to identify whether the request concerns actual spend, a forecast, available savings, realized savings, or workload autoscaler savings. Record cluster scope, currency, time range, and comparison period.

### Step 2: Validate the reporting basis

Use Grep across exported reports and runbooks to find baseline source, public versus adjusted prices, data gaps, and adoption thresholds. Cost comparison needs sufficient history; new clusters and low automation adoption can legitimately show incomplete or zero savings.

### Step 3: Reconcile cost layers

Compare provisioned resources, requested resources, utilization, lifecycle mix, price per resource, actual cost, and modeled baseline. When private discounts or commitments matter, require reviewed Price adjustments instead of assuming public list prices match the bill.

### Step 4: Rank opportunities by constraint

Group opportunities into workload rightsizing, node bin-packing, spot or fallback strategy, architecture choice, idle capacity, and allocation hygiene. For each, include savings confidence, SLO risk, prerequisite, owner, and evidence window.

### Step 5: Design a measured experiment

Use Write or Edit to create a canary hypothesis with a single policy change, expected capacity effect, performance guardrail, measurement window, and rollback. Do not combine node, vertical, horizontal, and pricing changes in one experiment.

### Step 6: Produce the decision record

State what CAST AI reports, what billing evidence confirms, what remains modeled, and which action is authorized. Preserve before-and-after snapshots without exporting sensitive workload names beyond their approved audience.

## Tool Discipline

Use Read for reports, billing extracts, and policy context. Use Grep to reconcile repeated cluster, workload, baseline, and pricing facts. Use Write and Edit only for the analysis, experiment, and decision record; this skill does not enable automation.

## Output

- Scope and reporting-basis statement
- Reconciled spend and savings table
- Ranked opportunities with confidence and risk
- One controlled experiment and rollback threshold

## Examples

A report shows high available savings but no realized savings because the cluster remains read-only. Another cluster shows modeled workload savings, but private prices are absent, so the team configures reviewed adjustments before using the number for a commitment.

## Error Handling

| Failure                            | Response                                                |
| ---------------------------------- | ------------------------------------------------------- |
| Baseline source is unknown         | Label savings unverified and obtain the report basis    |
| CAST AI and invoice periods differ | Normalize the window before comparison                  |
| Private pricing is missing         | Use Price adjustments or disclose list-price limitation |
| Optimization conflicts with an SLO | Reject the action regardless of modeled savings         |

## Resources

- [Cost evidence and source notes](references/official-docs.md)
- [Realized savings](https://docs.cast.ai/docs/savings-report)
- [Savings calculations](https://docs.cast.ai/docs/savings-baseline)
- [Price adjustments](https://docs.cast.ai/docs/discount-engine-overview)
