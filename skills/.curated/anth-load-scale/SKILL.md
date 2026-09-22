---
name: anth-load-scale
description: 'Implement load testing, auto-scaling, and capacity planning for Claude
  API.

  Use when running performance benchmarks, planning for traffic spikes,

  or configuring horizontal scaling for Claude-powered services.

  Trigger with phrases like "anthropic load test", "claude scaling",

  "anthropic capacity planning", "scale claude api".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- ai
- anthropic
compatibility: Designed for Claude Code
---
# Anthropic Load & Scale

## Overview

Capacity planning and load testing for Claude API integrations. Key constraint: your rate limits (RPM/ITPM/OTPM) are the ceiling, not your infrastructure.

## Capacity Planning

```python
# Calculate required tier based on traffic
def plan_capacity(
    requests_per_minute: int,
    avg_input_tokens: int,
    avg_output_tokens: int,
    model: str = "claude-sonnet-4-20250514"
) -> dict:
    itpm = requests_per_minute * avg_input_tokens
    otpm = requests_per_minute * avg_output_tokens

    # Estimate monthly cost
    pricing = {
        "claude-haiku-4-20250514": (0.80, 4.00),
        "claude-sonnet-4-20250514": (3.00, 15.00),
        "claude-opus-4-20250514": (15.00, 75.00),
    }
    rates = pricing[model]
    cost_per_request = (avg_input_tokens * rates[0] + avg_output_tokens * rates[1]) / 1_000_000
    monthly_cost = cost_per_request * requests_per_minute * 60 * 24 * 30

    return {
        "rpm_needed": requests_per_minute,
        "itpm_needed": itpm,
        "otpm_needed": otpm,
        "cost_per_request": f"${cost_per_request:.4f}",
        "monthly_estimate": f"${monthly_cost:,.0f}",
        "recommendation": "Contact Anthropic sales for Scale tier" if requests_per_minute > 500 else "Self-serve tiers sufficient",
    }

print(plan_capacity(100, 500, 200))
```

## Load Testing Script

```python
import anthropic
import asyncio
import time
from dataclasses import dataclass

@dataclass
class LoadTestResult:
    total_requests: int = 0
    successful: int = 0
    failed: int = 0
    rate_limited: int = 0
    avg_latency_ms: float = 0
    p99_latency_ms: float = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0

async def load_test(
    concurrency: int = 10,
    total_requests: int = 100,
    model: str = "claude-haiku-4-20250514"
) -> LoadTestResult:
    client = anthropic.Anthropic()
    result = LoadTestResult()
    latencies = []
    semaphore = asyncio.Semaphore(concurrency)

    async def single_request():
        async with semaphore:
            start = time.monotonic()
            try:
                msg = client.messages.create(
                    model=model,
                    max_tokens=64,
                    messages=[{"role": "user", "content": "Respond with exactly: OK"}]
                )
                duration = (time.monotonic() - start) * 1000
                latencies.append(duration)
                result.successful += 1
                result.total_input_tokens += msg.usage.input_tokens
                result.total_output_tokens += msg.usage.output_tokens
            except anthropic.RateLimitError:
                result.rate_limited += 1
            except Exception:
                result.failed += 1
            result.total_requests += 1

    tasks = [single_request() for _ in range(total_requests)]
    await asyncio.gather(*tasks)

    if latencies:
        latencies.sort()
        result.avg_latency_ms = sum(latencies) / len(latencies)
        result.p99_latency_ms = latencies[int(len(latencies) * 0.99)]

    return result

# Run: asyncio.run(load_test(concurrency=10, total_requests=50))
```

## Scaling Strategies

| Strategy | When | Implementation |
|----------|------|---------------|
| Queue-based processing | > 50 RPM sustained | Redis/SQS queue + worker pool |
| Model routing | Mixed workloads | Haiku for simple, Sonnet for complex |
| Message Batches | Offline processing | 100K requests, 50% cheaper, no RPM impact |
| Prompt caching | Repeated system prompts | 90% input token savings |
| Request coalescing | Duplicate prompts | Cache identical request hashes |

## Horizontal Scaling Pattern

```python
# Multiple application instances sharing the same API key
# Rate limits are per-organization, NOT per-instance
# Use a shared rate limiter (Redis) to coordinate

import redis

r = redis.Redis()

def check_rate_limit(key: str = "claude:rpm", limit: int = 100, window: int = 60) -> bool:
    current = r.incr(key)
    if current == 1:
        r.expire(key, window)
    return current <= limit
```

## Error Handling

| Issue | Cause | Fix |
|-------|-------|-----|
| 429 during load test | Exceeded tier limits | Reduce concurrency or upgrade tier |
| Increasing latency under load | Output queue saturation | Reduce max_tokens |
| Uneven request distribution | No load balancing | Use queue for fair distribution |

## Prerequisites

- Confirm the organization/model rate limits, budget ceiling, test environment, concurrency cap, and success/latency/error thresholds before measuring capacity.
- Run only against an approved sandbox using synthetic prompts and a no-op result sink. Never stress production or use real customer content for load tests.
- Configure aggregate metrics and redaction: request counts, status classes, latency, token totals, queue depth, and 429 counts are sufficient; prompts, completions, keys, and tool arguments are not.

## Instructions

1. Calculate RPM, input tokens per minute, output tokens per minute, concurrency, and expected cost from the measured workload. Reserve headroom below provider and application limits.
2. Start with a small canary, then increase concurrency in bounded steps while a shared limiter coordinates all workers. Stop immediately at error, budget, data-scope, or latency thresholds.
3. Separate real-time traffic from batch work, and use queue backpressure rather than unbounded task creation. Honor provider retry metadata and avoid synchronized retries.
4. Compare baseline and candidate metrics, including aggregate token/cost usage and `side_effects=0`. Promote only after an owner approves the result; revert autoscaling/limiter changes on regression.
5. Expire synthetic fixtures, queues, and temporary metrics according to the test retention policy, and keep a redacted capacity receipt.

## Output

Return a capacity receipt with workload class, model, concurrency steps, aggregate request/token counts, p50/p95/p99 latency, status/429 counts, queue depth, cost estimate, threshold decision, canary result, rollback reference, and cleanup status. Do not include payloads or secret material.

## Examples

Run 50 requests using `Respond with exactly: OK` in the sandbox, cap concurrency at 10, and assert `side_effects=0`. A useful receipt is `requests=50; successes=50; rate_limited=0; p99_ms=<redacted>; tokens=<aggregate>; canary=pass; cleanup=verified`.

## Resources

- [Rate Limits](https://platform.claude.com/docs/en/api/rate-limits)
- [Service Tiers](https://platform.claude.com/docs/en/api/service-tiers)

## Next Steps

For reliability patterns, see `anth-reliability-patterns`.
