---
name: clade-performance-tuning
description: "Optimize Anthropic API latency \u2014 streaming, prompt caching, model\
  \ selection,\nUse when working with performance-tuning patterns.\nconnection reuse,\
  \ and parallel requests.\nTrigger with \"anthropic slow\", \"claude latency\", \"\
  speed up anthropic\",\n\"anthropic performance\", \"claude response time\".\n"
allowed-tools: Read, Write, Edit
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- performance
- latency
compatibility: Designed for Claude Code
---
# Anthropic Performance Tuning

## Overview

Claude latency has two components: **time to first token (TTFT)** and **tokens per second (TPS)**. Different strategies target each.

## Latency Benchmarks (approximate)

| Model | TTFT (p50) | TTFT (p95) | Output TPS |
|-------|-----------|-----------|------------|
| Claude Haiku 4.5 | 200ms | 600ms | ~150 |
| Claude Sonnet 4 | 400ms | 1.2s | ~90 |
| Claude Opus 4 | 800ms | 2.5s | ~40 |

## Optimization Strategies

## Instructions

### Step 1: Always Stream

```typescript
// Streaming delivers the first token ASAP — user sees response instantly
// instead of waiting for the full response to generate

const stream = client.messages.stream({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  messages,
});

// First token arrives in ~400ms (Sonnet)
// Full response may take 5-10s, but user sees progress immediately
for await (const event of stream) {
  if (event.type === 'content_block_delta') {
    yield event.delta.text;
  }
}
```

### Step 2: Prompt Caching — Faster TTFT

```typescript
// Cached prompts skip re-processing — dramatically lower TTFT for large system prompts
const message = await client.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  system: [{
    type: 'text',
    text: largeSystemPrompt, // 10K+ tokens
    cache_control: { type: 'ephemeral' },
  }],
  messages,
}, {
  headers: { 'claude-beta': 'prompt-caching-2024-07-31' },
});
// TTFT drops from ~2s to ~500ms on cache hit with large prompts
```

### Step 3: Use Haiku for Speed-Critical Paths

```typescript
// Haiku is 2-4x faster than Sonnet with 80% quality for many tasks
// Use for: classification, extraction, simple Q&A, routing decisions

const route = await client.messages.create({
  model: 'claude-haiku-4-5-20251001', // 200ms TTFT
  max_tokens: 10,
  system: 'Classify the intent. Reply with exactly one word: search, create, update, delete.',
  messages: [{ role: 'user', content: userInput }],
});

// Then use Sonnet/Opus for the actual task
```

### Step 4: Reuse Client Instance

```typescript
// BAD — creates new connection pool per request
app.get('/api/chat', async (req, res) => {
  const client = new Anthropic(); // DON'T
  // ...
});

// GOOD — single client shared across requests
const client = new Anthropic(); // Module-level singleton

app.get('/api/chat', async (req, res) => {
  const message = await client.messages.create({ ... });
  // ...
});
```

### Step 5: Parallel Requests

```typescript
// When you need multiple independent Claude calls, fire them in parallel
const [summary, sentiment, entities] = await Promise.all([
  client.messages.create({ model: 'claude-haiku-4-5-20251001', max_tokens: 200,
    messages: [{ role: 'user', content: `Summarize: ${text}` }] }),
  client.messages.create({ model: 'claude-haiku-4-5-20251001', max_tokens: 20,
    messages: [{ role: 'user', content: `Sentiment (positive/negative/neutral): ${text}` }] }),
  client.messages.create({ model: 'claude-haiku-4-5-20251001', max_tokens: 200,
    messages: [{ role: 'user', content: `Extract named entities from: ${text}` }] }),
]);
```

### Step 6: Minimize Output Tokens

```typescript
// Fewer output tokens = faster response
system: 'Be extremely concise. Use bullet points, not paragraphs.',

// Set tight max_tokens
max_tokens: 256, // Don't use 4096 for short answers
```

## Output

- Streaming enabled for all user-facing responses (first token in ~400ms with Sonnet)
- Prompt caching reducing TTFT for large system prompts
- Model routing to Haiku for speed-critical classification/routing tasks
- Client instance reused across requests (no per-request connection overhead)
- Parallel requests firing independent Claude calls concurrently

## Error Handling

| Issue | Cause | Fix |
|-------|-------|-----|
| TTFT > 3s | Large uncached prompt | Enable prompt caching |
| Slow output | Using Opus for simple tasks | Downgrade to Haiku/Sonnet |
| Timeouts | Long generation + default timeout | `new Anthropic({ timeout: 120_000 })` |
| 529 overloaded | API capacity | SDK auto-retries; add fallback model |

## Examples

See Latency Benchmarks table and six numbered strategy sections above, each with complete TypeScript code examples.

## Resources

- [Streaming Docs](https://platform.claude.com/docs/en/build-with-claude/streaming)
- [Prompt Caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Models Comparison](https://platform.claude.com/docs/en/models/overview)

## Next Steps

See `clade-deploy-integration` for production deployment patterns.

## Prerequisites

- Completed `clade-install-auth`
- User-facing application where latency matters
- Understanding of streaming and async patterns
