---
name: windsurf-rate-limits
description: 'Analyze Devin Desktop (formerly Windsurf) quota limits, extra usage,
  and model-cost tradeoffs. Use when usage is blocked, a reset is unclear, or a team
  needs a current consumption plan. Trigger with phrases like "windsurf quota",
  "windsurf rate limit", "out of usage", "extra usage", or "windsurf model cost".'
argument-hint: "[plan and usage symptom]"
allowed-tools: Read, Grep
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- quota
- billing
- usage
compatibility: Designed for Claude Code
---

# Devin Desktop Quota and Usage

## Overview

Devin Desktop is the current name for Windsurf. Its current usage system uses daily and weekly quota; optional extra usage can continue work after included quota is exhausted.

## Prerequisites

- The user's current plan and reset time from the in-product usage meter
- Permission to view billing only when account-level diagnosis is requested
- A task or session sample representative of the reported consumption

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Grep` to locate relevant settings, rules, logs, or code without broad collection.

## Instructions

### Step 1: Identify the applicable plan

Read the plan page instead of assuming a legacy tier or price. Record whether the account is Free, Pro, Max, Teams, Enterprise, or a grandfathered plan.

### Step 2: Read the usage meter

Capture without credentials:

- remaining daily quota and reset time, when present;
- remaining weekly quota and reset time;
- whether extra usage is enabled and its configured limit;
- the model and speed option used when the issue occurred.

Paid plans and full seats can have included allowances. Free accounts wait for reset; eligible paid accounts can use configured extra usage after quota.

### Step 3: Explain what consumes quota

Usage is token-based and varies by model. Long shared timelines, large context, tool calls, output, and fast or priority variants can increase consumption. Free models do not count against quota. Do not publish a fixed per-prompt conversion table.

### Step 4: Choose the least-cost correction

1. Start a focused conversation when old context is no longer needed.
2. Scope repository context and attachments to the task.
3. Use a lower-cost SWE-family model, such as a currently available SWE model, for routine work.
4. Keep frontier or fast variants for tasks that justify their higher consumption.
5. Configure extra-usage limits only with the billing owner's approval.

### Step 5: Handle legacy credit language

Treat "prompt credits" as the retired built-in system. Historical add-on credits were converted to extra-usage balance under the migration rules. Current self-serve Devin billing also uses on-demand credits outside included quota; do not confuse those billing credits with the retired per-prompt Windsurf allocation.

### Step 6: Verify

Run one representative, non-destructive request and confirm the meter behaves as expected. If usage remains unavailable, preserve the displayed error and reset time and route it to account support.

## Output

Provide a current usage diagnosis naming the plan, daily or weekly quota state, extra-usage or on-demand balance state, affected surface, displayed reset timing, and least-cost next action. Label any amount copied from the product with its observation date.

## Error Handling

| Symptom | Response |
|---|---|
| Usage meter unavailable | Re-authenticate, confirm organization, and use the plan page |
| Quota exhausted | Wait for reset or use approved extra usage on an eligible plan |
| Unexpected drain | Compare model, speed, context size, and tool-heavy steps |
| Billing terms conflict | Prefer the current quota page and plan page; note grandfathered terms |

Never infer a user's balance from a public pricing page, and never request screenshots containing payment details or session tokens.

## Examples

**Diagnosis:** "Pro plan; daily quota exhausted, weekly quota remains; reset shown at midnight local time. Extra usage is disabled. Use a lower-cost SWE model after reset and split the repository-wide request into bounded tasks."

**Team control:** "Full-seat quota is included; on-demand usage needs billing-owner approval. Set an account spending limit before enabling it."

## Resources

- [Focused first-party references](references/official-docs.md)
- [Quota-based usage](https://docs.devin.ai/desktop/accounts/quota)
- [Current self-serve plans](https://docs.devin.ai/admin/billing/self-serve)
- [Usage accounting](https://docs.devin.ai/admin/billing/usage)
- [Manage plan](https://windsurf.com/subscription/manage-plan)

## Related Skill

Continue with `windsurf-cost-tuning` to convert quota evidence into reviewed team seat allocation, extra-usage policy, and recurring budget analysis.
