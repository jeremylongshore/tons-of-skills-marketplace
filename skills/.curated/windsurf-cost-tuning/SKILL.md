---
name: windsurf-cost-tuning
description: 'Optimize Devin Desktop (formerly Windsurf) licensing through current
  plan, seat, quota, and extra-usage analysis. Use when right-sizing a team,
  forecasting usage, or reducing spend. Trigger with "windsurf cost", "windsurf
  billing", "seat audit", "extra usage", or "windsurf budget".'
argument-hint: "[team size, plan, and usage period]"
allowed-tools: Read, Grep
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- cost-optimization
- licensing
- teams
compatibility: Designed for Claude Code
---

# Devin Desktop Cost Tuning

## Overview

Devin Desktop is the current name for Windsurf. Optimize the combined Devin subscription using current plan terms, full and flex seats, included daily or weekly quota, and approved on-demand or extra usage.

## Prerequisites

- Current plan and invoice period
- Member roster with full or flex seat assignment
- Usage observations for a representative four-week period
- Billing-owner approval for any plan, seat, or spending-limit change

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Grep` to locate relevant settings, rules, logs, or code without broad collection.

## Instructions

### Step 1: Establish current terms

Open the current plan page and record the observation date. Do not copy a static price table into durable policy; grandfathered and enterprise contracts can differ from public self-serve plans.

### Step 2: Classify members

For each member, capture role, eligible surfaces, active days, included-quota use, on-demand use, and business-critical workflows. Avoid judging value from prompt volume alone.

### Step 3: Model seat allocation

- Use a full seat for regular users who need Devin Desktop and included quota.
- Use a flex seat only where current plan terms support the required surfaces and occasional usage.
- Remove or reassign seats for departed or persistently inactive members through the documented admin workflow.
- Preserve minimum commitments and contract constraints in the calculation.

### Step 4: Control variable usage

1. Set approved on-demand or extra-usage limits.
2. Use lower-cost SWE-family models for routine work.
3. Start focused sessions instead of carrying irrelevant context.
4. Reserve frontier and fast variants for work whose value justifies their cost.
5. Review exceptions with the billing owner rather than silently disabling productive users.

### Step 5: Calculate scenarios

Compare the status quo with at least two alternatives. For each scenario include recurring seats, plan minimums, expected variable usage, migration cost, productivity risk, and confidence level.

### Step 6: Pilot and verify

Apply changes to a small cohort for one billing cycle. Compare delivery, incident, and satisfaction signals alongside usage; roll back allocations that create operational harm.

## Output

Deliver a dated cost-and-usage brief with current plan assumptions, full and flex seat allocation, included quota utilization, on-demand or extra-usage exposure, scenario totals, confidence, and prioritized actions. Link current pricing instead of freezing mutable amounts.

## Error Handling

| Problem | Response |
|---|---|
| Invoice and public pricing disagree | Treat the invoice or contract as authoritative and note grandfathering |
| Usage data is incomplete | Report coverage and avoid annualizing a partial period without a range |
| Member appears inactive | Confirm role, leave, and alternate surfaces before changing access |
| Savings reduce delivery quality | Restore the prior allocation and document the failed hypothesis |

Never expose member-level activity outside the authorized audience.

## Examples

**Recommendation:** "Keep 18 full seats for daily users, test flex seats for 6 occasional users, cap shared on-demand usage, and review after one full billing cycle. Expected savings are a range because enterprise terms were not supplied."

## Resources

- [Focused first-party references](references/official-docs.md)
- [Current self-serve plans](https://docs.devin.ai/admin/billing/self-serve)
- [Usage accounting](https://docs.devin.ai/admin/billing/usage)
- [Quota-based usage](https://docs.devin.ai/desktop/accounts/quota)
- [Manage plan](https://windsurf.com/subscription/manage-plan)

## Related Skill

Use `windsurf-observability` to define trustworthy adoption, latency, quota, and outcome evidence for the next recurring cost review.
