---
name: anth-cost-tuning
description: 'Optimize Anthropic Claude API costs with model routing, prompt caching,

  batching, and spend monitoring.

  Use when analyzing Claude API billing, reducing costs,

  or implementing cost controls and budget alerts.

  Trigger with phrases like "anthropic cost", "claude billing",

  "reduce claude spend", "anthropic budget", "claude pricing optimize".

  '
allowed-tools: Read, Write, Edit, Grep
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- ai
- anthropic
compatibility: Designed for Claude Code
---
# Anthropic Cost Tuning

## Overview

Optimize Claude API spend through model routing, prompt caching, the Message Batches API, and real-time cost tracking. The four biggest levers: model selection (4-19x), prompt caching (10x input), batches (2x), and `max_tokens` discipline.

## Pricing Reference (per million tokens)

| Model | Input | Output | Cache Read | Cache Write |
|-------|-------|--------|------------|-------------|
| Claude Haiku | $0.80 | $4.00 | $0.08 | $1.00 |
| Claude Sonnet | $3.00 | $15.00 | $0.30 | $3.75 |
| Claude Opus | $15.00 | $75.00 | $1.50 | $18.75 |

**Message Batches:** 50% off all model pricing for async processing.

## Cost Calculator

```python
def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = "claude-sonnet-4-20250514",
    cached_input: int = 0,
    use_batch: bool = False
) -> float:
    pricing = {
        "claude-haiku-4-20250514": {"input": 0.80, "output": 4.00, "cache_read": 0.08},
        "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00, "cache_read": 0.30},
        "claude-opus-4-20250514": {"input": 15.00, "output": 75.00, "cache_read": 1.50},
    }
    rates = pricing[model]
    uncached_input = input_tokens - cached_input

    cost = (
        uncached_input * rates["input"] +
        cached_input * rates["cache_read"] +
        output_tokens * rates["output"]
    ) / 1_000_000

    if use_batch:
        cost *= 0.5

    return cost

# Example: 10K requests/day, 500 input + 200 output tokens each
daily = estimate_cost(500, 200, "claude-sonnet-4-20250514") * 10_000
print(f"Daily: ${daily:.2f}")      # ~$0.045 * 10K = $450/day
print(f"Monthly: ${daily * 30:.2f}")  # ~$13,500/month

# Same with Haiku + batching
daily_optimized = estimate_cost(500, 200, "claude-haiku-4-20250514", use_batch=True) * 10_000
print(f"Optimized: ${daily_optimized:.2f}/day")  # ~$22/day (20x cheaper)
```

## Strategy 1: Model Routing

```python
def route_to_model(task: str, complexity: str) -> str:
    """Route tasks to cheapest adequate model."""
    # Haiku: classification, extraction, yes/no, routing ($0.80/$4)
    if task in ("classify", "extract", "route", "validate"):
        return "claude-haiku-4-20250514"

    # Sonnet: general tasks, code, tool use ($3/$15)
    if complexity in ("low", "medium"):
        return "claude-sonnet-4-20250514"

    # Opus: only for complex reasoning, research ($15/$75)
    return "claude-opus-4-20250514"
```

## Strategy 2: Prompt Caching

```python
# Cache system prompts and reference documents (90% input savings)
# Break-even: 2 requests with same cached content
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=256,
    system=[{
        "type": "text",
        "text": large_reference_document,  # 10K+ tokens
        "cache_control": {"type": "ephemeral"}
    }],
    messages=[{"role": "user", "content": user_question}]
)
```

## Strategy 3: Batches for Non-Real-Time

```python
# 50% cost reduction for anything that doesn't need immediate response
# Ideal for: summarization pipelines, data extraction, content generation
batch = client.messages.batches.create(requests=[...])  # Up to 100K requests
```

## Strategy 4: Spend Tracking

```python
import anthropic
from dataclasses import dataclass, field

@dataclass
class SpendTracker:
    budget_usd: float = 100.0
    spent_usd: float = 0.0
    requests: int = 0

    def track(self, response):
        cost = estimate_cost(
            response.usage.input_tokens,
            response.usage.output_tokens,
            response.model,
            getattr(response.usage, "cache_read_input_tokens", 0)
        )
        self.spent_usd += cost
        self.requests += 1

        if self.spent_usd > self.budget_usd * 0.8:
            print(f"WARNING: 80% budget used (${self.spent_usd:.2f}/${self.budget_usd})")
        if self.spent_usd > self.budget_usd:
            raise RuntimeError(f"Budget exceeded: ${self.spent_usd:.2f}")

tracker = SpendTracker(budget_usd=50.0)
```

## Cost Reduction Checklist

- [ ] Use Haiku for classification/extraction/routing tasks
- [ ] Enable prompt caching for repeated system prompts
- [ ] Use Message Batches for non-real-time processing
- [ ] Set `max_tokens` to realistic values (not maximum)
- [ ] Use prefill to reduce output preamble tokens
- [ ] Implement spend tracking and budget alerts
- [ ] Monitor via [Usage API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api)

## Prerequisites

- Establish an approved budget, billing owner, cost allocation dimensions, and alert thresholds before changing model routing or batch behavior.
- Use a sandbox workspace, synthetic prompts, pinned model IDs, and a versioned pricing snapshot; confirm current rates in the official pricing documentation before making a forecast.
- Configure least-privileged credentials and ensure logs/metrics contain token counts and aggregate cost only, never prompt or response content.

## Instructions

1. Baseline request volume, input/output/cache tokens, latency, quality, and spend by feature using a redacted measurement window. Do not make routing changes from a single outlier.
2. Define a quality floor and route only eligible workloads to the least expensive model that meets it. Use prompt caching only for approved non-sensitive content and batches only where asynchronous completion is acceptable.
3. Cap `max_tokens`, concurrency, retries, and batch size. Enforce per-feature and per-workspace budgets before requests are sent; fail closed when a budget or scope check cannot be evaluated.
4. Test the proposed policy on synthetic fixtures in a sandbox, then canary it with aggregate cost, quality, latency, error, and rate-limit monitoring. Require owner approval before broader rollout.
5. If quality, spend, or policy thresholds regress, disable the new route/cache/batch policy, restore the prior configuration, and retain a redacted comparison receipt.

## Output

Produce a cost-control receipt containing the pricing snapshot date, policy version, model/batch/cache decisions, token aggregates, projected and observed spend, quality and latency results, budget outcome, canary scope, approval, and rollback reference. Exclude prompt/response text, customer identifiers, API keys, and raw billing exports.

## Error Handling

| Failure | Response |
|---|---|
| Unknown model price or usage field | Stop forecasting, refresh the official pricing/usage source, and mark the estimate provisional. |
| Budget or quota exceeded | Reject or queue new work, alert the owner, and do not bypass the guard with another key or workspace. |
| Quality regression after cheaper routing | Restore the prior route, quarantine affected output, and rerun the quality fixture before another canary. |
| Cache or batch unsuitable for data/latency policy | Disable that optimization and use the approved synchronous, non-cached path. |

## Examples

Evaluate 1,000 synthetic classification prompts in a sandbox with a fixed budget, compare pinned Sonnet against Haiku plus an approved batch policy, assert `customer_content_logged=0`, and emit `budget=within_limit; quality=pass; canary=internal; rollback=route-v1`. Do not use live customer prompts to tune pricing.

## Resources

- [Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [Prompt Caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Usage & Cost API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api)
- [Message Batches](https://platform.claude.com/docs/en/api/messages/batches/create)

## Next Steps

For architecture patterns, see `anth-reference-architecture`.
