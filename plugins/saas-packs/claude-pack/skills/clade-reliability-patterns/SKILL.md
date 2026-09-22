---
name: clade-reliability-patterns
description: "Build fault-tolerant Claude integrations \u2014 retries, circuit breakers,\n\
  Use when working with reliability-patterns patterns.\nfallbacks, timeouts, and graceful\
  \ degradation.\nTrigger with \"anthropic reliability\", \"claude fault tolerance\"\
  ,\n\"anthropic circuit breaker\", \"claude fallback\".\n"
allowed-tools: Read, Write, Edit
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- reliability
- resilience
compatibility: Designed for Claude Code
---
# Anthropic Reliability Patterns

## Overview

Build fault-tolerant Claude integrations with built-in SDK retries, model fallback chains (Sonnet → Haiku), circuit breakers to avoid hammering a failing API, graceful degradation with cached/static responses, and per-request timeout configuration.

## Built-In SDK Retries

The SDK retries 429 (rate limit) and 529 (overloaded) automatically:

```typescript
const client = new Anthropic({
  maxRetries: 3, // default: 2
  timeout: 120_000, // 2 minutes
});
```

## Model Fallback Chain

```typescript
const FALLBACK_CHAIN = ['claude-sonnet-4-20250514', 'claude-haiku-4-5-20251001'];

async function callWithFallback(params: Anthropic.MessageCreateParams) {
  for (const model of FALLBACK_CHAIN) {
    try {
      return await client.messages.create({ ...params, model });
    } catch (err) {
      if (err instanceof Anthropic.APIError && err.status >= 500) {
        console.warn(`${model} failed (${err.status}), trying next...`);
        continue;
      }
      throw err; // Don't retry client errors (4xx)
    }
  }
  throw new Error('All models failed');
}
```

## Circuit Breaker

```typescript
class ClaudeCircuitBreaker {
  private failures = 0;
  private lastFailure = 0;
  private readonly threshold = 5;
  private readonly resetMs = 60_000;

  async call(params: Anthropic.MessageCreateParams) {
    if (this.failures >= this.threshold && Date.now() - this.lastFailure < this.resetMs) {
      throw new Error('Circuit open — Claude API unavailable');
    }

    try {
      const result = await client.messages.create(params);
      this.failures = 0;
      return result;
    } catch (err) {
      if (err instanceof Anthropic.APIError && err.status >= 500) {
        this.failures++;
        this.lastFailure = Date.now();
      }
      throw err;
    }
  }
}
```

## Graceful Degradation

```typescript
async function getResponse(userInput: string): Promise<string> {
  try {
    const message = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1024,
      messages: [{ role: 'user', content: userInput }],
    });
    return message.content[0].text;
  } catch (err) {
    // Return cached/static response instead of failing
    console.error('Claude unavailable, using fallback');
    return "I'm temporarily unable to process your request. Please try again shortly.";
  }
}
```

## Timeout Handling

```typescript
const client = new Anthropic({
  timeout: 30_000, // 30s for most requests
});

// Override per-request for long-running tasks
const message = await client.messages.create(params, {
  timeout: 120_000, // 2 minutes for complex prompts
});
```

## Output

- SDK configured with appropriate `maxRetries` and `timeout`
- Model fallback chain automatically trying cheaper models on failure
- Circuit breaker preventing cascading failures during outages
- Graceful degradation returning static responses when Claude is unavailable

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| API Error | Check error type and status code | See `clade-common-errors` |

## Examples

See Built-In SDK Retries, Model Fallback Chain, Circuit Breaker class, Graceful Degradation handler, and Timeout Handling above.

## Resources

- [Error Types](https://platform.claude.com/docs/en/api/errors)
- SDK Retries

## Next Steps

See `clade-policy-guardrails` for content safety patterns.

## Prerequisites

- Completed `clade-install-auth`
- Production Claude integration requiring high availability
- Understanding of fault tolerance patterns (retries, circuit breakers)

## Instructions

### Step 1: Review the patterns below

Each section contains production-ready code examples. Copy and adapt them to your use case.

### Step 2: Apply to your codebase

Integrate the patterns that match your requirements. Test each change individually.

### Step 3: Verify

Run your test suite to confirm the integration works correctly.
