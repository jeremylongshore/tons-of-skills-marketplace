---
name: anth-rate-limits
description: 'Implement Anthropic Claude API rate limiting, backoff, and quota management.

  Use when handling 429 errors, optimizing request throughput,

  or managing RPM/TPM limits across usage tiers.

  Trigger with phrases like "anthropic rate limit", "claude 429",

  "anthropic throttling", "claude retry", "anthropic backoff".

  '
allowed-tools: Read, Write, Edit
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- ai
- anthropic
compatibility: Designed for Claude Code
---
# Anthropic Rate Limits

## Overview

The Claude API uses token-bucket rate limiting measured in three dimensions: requests per minute (RPM), input tokens per minute (ITPM), and output tokens per minute (OTPM). Limits increase automatically as you move through usage tiers.

## Rate Limit Dimensions

| Dimension | Header | Description |
|-----------|--------|-------------|
| RPM | `anthropic-ratelimit-requests-limit` | Requests per minute |
| ITPM | `anthropic-ratelimit-tokens-limit` | Input tokens per minute |
| OTPM | `anthropic-ratelimit-tokens-limit` | Output tokens per minute |

Limits are per-organization and per-model-class. Cached input tokens do NOT count toward ITPM limits.

## Usage Tiers (Auto-Upgrade)

| Tier | Monthly Spend | Key Benefit |
|------|---------------|-------------|
| Tier 1 (Free) | $0 | Evaluation access |
| Tier 2 | $40+ | Higher RPM |
| Tier 3 | $200+ | Production-grade limits |
| Tier 4 | $2,000+ | High-throughput access |
| Scale | Custom | Custom limits via sales |

Check your current tier and limits at [console.anthropic.com](https://console.anthropic.com/settings/limits).

## SDK Built-In Retry

```python
import anthropic

# The SDK retries 429 and 5xx errors automatically (2 retries by default)
client = anthropic.Anthropic(max_retries=5)  # Increase for high-traffic apps

# Disable auto-retry for manual control
client = anthropic.Anthropic(max_retries=0)
```

```typescript
const client = new Anthropic({ maxRetries: 5 });
```

## Custom Rate Limiter with Header Awareness

```python
import time
import anthropic

class RateLimitedClient:
    def __init__(self):
        self.client = anthropic.Anthropic(max_retries=0)  # We handle retries
        self.remaining_requests = 100
        self.remaining_tokens = 100000
        self.reset_at = 0.0

    def create_message(self, **kwargs):
        # Pre-check: wait if near limit
        if self.remaining_requests < 3 and time.time() < self.reset_at:
            wait = self.reset_at - time.time()
            print(f"Pre-throttle: waiting {wait:.1f}s")
            time.sleep(wait)

        for attempt in range(5):
            try:
                response = self.client.messages.create(**kwargs)

                # Update from response headers (via _response)
                headers = response._response.headers
                self.remaining_requests = int(headers.get("anthropic-ratelimit-requests-remaining", 100))
                self.remaining_tokens = int(headers.get("anthropic-ratelimit-tokens-remaining", 100000))
                reset = headers.get("anthropic-ratelimit-requests-reset")
                if reset:
                    from datetime import datetime
                    self.reset_at = datetime.fromisoformat(reset.replace("Z", "+00:00")).timestamp()

                return response
            except anthropic.RateLimitError as e:
                retry_after = float(e.response.headers.get("retry-after", 2 ** attempt))
                print(f"429 — retry in {retry_after}s (attempt {attempt + 1})")
                time.sleep(retry_after)

        raise Exception("Exhausted rate limit retries")
```

## Queue-Based Throughput Control

```typescript
import PQueue from 'p-queue';
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

// Enforce 50 RPM with concurrency limit
const queue = new PQueue({
  concurrency: 10,
  interval: 60_000,
  intervalCap: 50,
});

async function rateLimitedCall(prompt: string) {
  return queue.add(() =>
    client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1024,
      messages: [{ role: 'user', content: prompt }],
    })
  );
}

// Process 200 prompts without hitting limits
const results = await Promise.all(
  prompts.map(p => rateLimitedCall(p))
);
```

## Cost-Saving: Use Batches for Bulk Work

```python
# Message Batches API: 50% cheaper, no rate limit pressure on real-time quota
batch = client.messages.batches.create(
    requests=[
        {"custom_id": f"req-{i}", "params": {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        }}
        for i, prompt in enumerate(prompts)
    ]
)
```

## Error Handling

| Header | Description | Action |
|--------|-------------|--------|
| `retry-after` | Seconds until next request allowed | Sleep this duration exactly |
| `anthropic-ratelimit-requests-remaining` | Requests left in window | Throttle if < 5 |
| `anthropic-ratelimit-tokens-remaining` | Tokens left in window | Reduce `max_tokens` if low |
| `anthropic-ratelimit-requests-reset` | ISO timestamp of window reset | Schedule retry after this time |

## Prerequisites

- Record the authorized organization/model limits, budget ceiling, retry cap, and shared limiter policy. Do not infer a production limit from a local load test.
- Use synthetic prompts and a sandbox workspace for experiments, with no-op downstream effects and aggregate-only telemetry.
- Ensure logs exclude API keys, prompts, completions, tool arguments, and user identifiers; retain only headers needed to explain throttling, request IDs, and counts.

## Instructions

1. Read the response headers after each permitted call and update a shared limiter using the provider's remaining/reset values. Reserve headroom for interactive traffic.
2. Honor `retry-after` when present, apply jitter and a maximum delay, and stop after a bounded number of attempts. Never let every worker retry at the same instant.
3. Coordinate RPM, input-token, and output-token budgets across instances. Queue or batch offline work and apply backpressure when the shared budget is exhausted.
4. Canary limiter changes with synthetic traffic and compare 429 rate, latency, queue age, token totals, and `side_effects=0`. Roll back the limiter/configuration if thresholds or scope checks fail.
5. Expire queued test items and temporary counters according to the retention policy; retain a redacted receipt for the decision.

## Output

Produce a rate-limit receipt with model class, configured and observed aggregate limits, limiter version, request/token counts, retry-after handling, 429 count, queue/batch disposition, canary result, rollback reference, and cleanup status. Do not include payloads or secrets.

## Examples

Queue 20 synthetic `OK` prompts behind a shared 10-RPM limiter, permit only the configured window, and assert `429_retries_bounded=true; side_effects=0`. The receipt may contain `submitted=20; completed=<aggregate>; deferred=<aggregate>; headers_captured=true; canary=pass; cleanup=verified` without user content.

## Resources

- [Rate Limits Documentation](https://platform.claude.com/docs/en/api/rate-limits)
- [Usage Tiers](https://platform.claude.com/docs/en/api/service-tiers)
- [Message Batches API](https://platform.claude.com/docs/en/api/messages/batches/create)

## Next Steps

For security configuration, see `anth-security-basics`.
