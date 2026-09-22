---
name: clade-observability
description: "Monitor Claude API calls \u2014 log tokens, latency, costs, errors,\
  \ and\nUse when working with observability patterns.\nset up alerts for production\
  \ Claude integrations.\nTrigger with \"anthropic monitoring\", \"claude observability\"\
  ,\n\"track claude usage\", \"anthropic logging\".\n"
allowed-tools: Read, Write, Edit
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- monitoring
- observability
compatibility: Designed for Claude Code
---
# Anthropic Observability

## Overview

Every `messages.create` call should be instrumented. Track tokens, latency, cost, model, and errors.

## Logging Wrapper

```typescript
import Anthropic from '@claude-ai/sdk';

const client = new Anthropic();

async function trackedCreate(params: Anthropic.MessageCreateParams) {
  const start = performance.now();
  try {
    const message = await client.messages.create(params);
    const durationMs = Math.round(performance.now() - start);

    const log = {
      timestamp: new Date().toISOString(),
      model: message.model,
      input_tokens: message.usage.input_tokens,
      output_tokens: message.usage.output_tokens,
      cache_read_tokens: message.usage.cache_read_input_tokens || 0,
      duration_ms: durationMs,
      stop_reason: message.stop_reason,
      estimated_cost: estimateCost(message.model, message.usage),
    };
    console.log('anthropic_request', JSON.stringify(log));

    return message;
  } catch (err) {
    const durationMs = Math.round(performance.now() - start);
    console.error('anthropic_error', JSON.stringify({
      timestamp: new Date().toISOString(),
      model: params.model,
      error_type: err instanceof Anthropic.APIError ? err.error?.type : 'unknown',
      status: err instanceof Anthropic.APIError ? err.status : null,
      request_id: err instanceof Anthropic.APIError ? err.headers?.['request-id'] : null,
      duration_ms: durationMs,
    }));
    throw err;
  }
}

function estimateCost(model: string, usage: Anthropic.Usage): number {
  const rates: Record<string, [number, number]> = {
    'claude-opus-4-20250514': [15, 75],
    'claude-sonnet-4-20250514': [3, 15],
    'claude-haiku-4-5-20251001': [0.80, 4],
  };
  const [inputRate, outputRate] = rates[model] || [3, 15];
  return (usage.input_tokens * inputRate + usage.output_tokens * outputRate) / 1_000_000;
}
```

## Key Metrics to Track

| Metric | Source | Alert Threshold |
|--------|--------|----------------|
| Error rate | error logs | > 5% over 5 minutes |
| p95 latency | duration_ms | > 10s (Sonnet) |
| Daily cost | estimated_cost sum | > 2x daily average |
| 429 rate | error_type = rate_limit | > 10/minute |
| 529 rate | error_type = overloaded | > 5/minute |
| Token usage | input_tokens + output_tokens | > daily budget |

## Anthropic Console Monitoring

- **Usage dashboard**: console.anthropic.com → Usage
- **Spending limits**: console.anthropic.com → Settings → Limits
- **API logs**: Not available via API — use your own logging

## Output

- Every Claude API call logged with tokens, latency, cost estimate, and model
- Error calls logged with request ID, status code, and error type
- Metrics dashboarded: error rate, p95 latency, daily cost, 429/529 rates
- Spending alerts configured in Anthropic console

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| API Error | Check error type and status code | See `clade-common-errors` |

## Examples

See Logging Wrapper with `trackedCreate()`, `estimateCost()` function, Key Metrics table with alert thresholds, and Anthropic Console Monitoring section above.

## Resources

- [Usage Dashboard](https://console.anthropic.com/settings/usage)
- [Rate Limits](https://platform.claude.com/docs/en/api/rate-limits)

## Next Steps

See `clade-incident-runbook` for when things go wrong.

## Prerequisites

- Completed `clade-install-auth`
- Logging infrastructure (console, structured logs, or observability platform)
- Production Claude integration to monitor

## Instructions

### Step 1: Review the patterns below

Each section contains production-ready code examples. Copy and adapt them to your use case.

### Step 2: Apply to your codebase

Integrate the patterns that match your requirements. Test each change individually.

### Step 3: Verify

Run your test suite to confirm the integration works correctly.
