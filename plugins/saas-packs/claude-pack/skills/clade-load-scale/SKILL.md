---
name: clade-load-scale
description: "Scale Claude usage for high-throughput applications \u2014 batches,\
  \ queues,\nUse when working with load-scale patterns.\nconcurrency control, and\
  \ tier upgrades.\nTrigger with \"anthropic scale\", \"claude high volume\", \"anthropic\
  \ throughput\",\n\"scale claude api\", \"anthropic concurrent requests\".\n"
allowed-tools: Read, Write, Edit
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- scale
- throughput
compatibility: Designed for Claude Code
---
# Anthropic Load & Scale

## Overview

Scale Claude usage for high-throughput applications. Covers four strategies: Message Batches (10K requests, 50% off, no rate limits), request queues with concurrency control via p-limit, tier upgrades (Tier 1-4 + Scale), and model selection for throughput (Haiku is 3-4x faster than Sonnet).

## Scaling Strategies

## Instructions

### Step 1: Message Batches (Best for Bulk)

```typescript
// 10K requests per batch, 50% cheaper, no rate limits
const batch = await client.messages.batches.create({
  requests: items.map((item, i) => ({
    custom_id: `${i}`,
    params: { model: 'claude-sonnet-4-20250514', max_tokens: 1024, messages: [{ role: 'user', content: item }] },
  })),
});
// Process up to 100 concurrent batches
```

### Step 2: Request Queue with Concurrency Control

```typescript
import pLimit from 'p-limit';

// Match your rate limit tier
const limit = pLimit(10); // 10 concurrent requests

const results = await Promise.all(
  inputs.map(input =>
    limit(() => client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1024,
      messages: [{ role: 'user', content: input }],
    }))
  )
);
```

### Step 3: Tier Upgrades

Increase your spending to unlock higher tiers:

| Tier | RPM | Input TPM | How to Qualify |
|------|-----|-----------|----------------|
| 1 | 50 | 40K | Free |
| 2 | 1,000 | 80K | $40+ total spend |
| 3 | 2,000 | 160K | $200+ total spend |
| 4 | 4,000 | 400K | $400+ total spend |
| Scale | Custom | Custom | Contact sales |

### Step 4: Model Selection for Throughput

```typescript
// Haiku processes 3-4x faster than Sonnet, 8x faster than Opus
// Use the fastest model that meets quality requirements
const model = taskComplexity === 'simple' ? 'claude-haiku-4-5-20251001' : 'claude-sonnet-4-20250514';
```

## Monitoring at Scale

```typescript
// Track throughput metrics
let requestCount = 0;
let tokenCount = 0;

setInterval(() => {
  console.log(`Throughput: ${requestCount} req/min, ${tokenCount} tokens/min`);
  requestCount = 0;
  tokenCount = 0;
}, 60_000);
```

## Output

- Batch processing configured for bulk workloads (50% cheaper, no rate limits)
- Concurrency-controlled request queue matching rate limit tier
- Rate limit tier upgraded by increasing cumulative spend
- Throughput metrics tracked (requests/min, tokens/min)

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| API Error | Check error type and status code | See `clade-common-errors` |

## Examples

See Message Batches example, p-limit concurrency control, Tier Upgrades table, and Monitoring at Scale metrics tracking above.

## Resources

- [Rate Limits](https://platform.claude.com/docs/en/api/rate-limits)
- [Message Batches](https://platform.claude.com/docs/en/api/messages/batches/create)

## Next Steps

See `clade-reliability-patterns` for fault-tolerant high-scale patterns.

## Prerequisites

- Completed `clade-rate-limits` for understanding tier limits
- High-volume use case requiring more than basic tier throughput
- For batches: tolerance for async processing (24h SLA)
