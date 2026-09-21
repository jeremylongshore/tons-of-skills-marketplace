---
name: clade-cost-tuning
description: "Optimize Anthropic API costs \u2014 model selection, prompt caching,\
  \ batches,\nUse when working with cost-tuning patterns.\ntoken reduction, and usage\
  \ monitoring.\nTrigger with \"anthropic pricing\", \"claude cost\", \"reduce anthropic\
  \ spend\",\n\"anthropic billing\", \"claude cheaper\".\n"
allowed-tools: Read, Write, Edit
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- cost
- pricing
compatibility: Designed for Claude Code
---
# Anthropic Cost Tuning

## Overview

Anthropic charges per token. Input tokens, output tokens, and cached tokens each have different prices. Here's how to minimize cost without losing quality.

## Pricing (per million tokens)

| Model | Input | Output | Cached Input | Batch Input | Batch Output |
|-------|-------|--------|-------------|-------------|--------------|
| Claude Opus 4 | $15.00 | $75.00 | $1.50 | $7.50 | $37.50 |
| Claude Sonnet 4 | $3.00 | $15.00 | $0.30 | $1.50 | $7.50 |
| Claude Haiku 4.5 | $0.80 | $4.00 | $0.08 | $0.40 | $2.00 |

## Cost Reduction Strategies

## Instructions

### Step 1: Right-Size Your Model

```typescript
// DON'T use Opus for everything
// DO match model to task complexity:

// Simple classification/extraction → Haiku (cheapest)
const category = await classify(text, 'claude-haiku-4-5-20251001');

// General coding/writing → Sonnet (balanced)
const code = await generate(spec, 'claude-sonnet-4-20250514');

// Complex multi-step reasoning → Opus (best quality)
const analysis = await analyze(data, 'claude-opus-4-20250514');
```

### Step 2: Prompt Caching (90% off input tokens)

```typescript
// Cache your system prompt — pays for itself after 2 calls
const message = await client.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  system: [{
    type: 'text',
    text: longSystemPrompt, // Must be 1024+ tokens
    cache_control: { type: 'ephemeral' }, // Cache for 5 minutes
  }],
  messages,
}, {
  headers: { 'claude-beta': 'prompt-caching-2024-07-31' },
});

// First call: cache_creation_input_tokens charged at 1.25x
// Subsequent calls: cache_read_input_tokens charged at 0.1x (90% savings!)
```

### Step 3: Message Batches (50% off everything)

```typescript
// For non-urgent work — 50% cheaper, 24h processing SLA
const batch = await client.messages.batches.create({
  requests: prompts.map((p, i) => ({
    custom_id: `job-${i}`,
    params: {
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1024,
      messages: [{ role: 'user', content: p }],
    },
  })),
});
// Sonnet: $1.50/$7.50 per MTok instead of $3/$15
```

### Step 4: Reduce Token Count

```typescript
// Trim conversation history — keep system + last N turns
function trimMessages(messages: MessageParam[], maxTurns = 10) {
  if (messages.length <= maxTurns * 2) return messages;
  return messages.slice(-(maxTurns * 2));
}

// Set tight max_tokens — don't pay for output you won't use
const message = await client.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 256, // Not 4096 if you only need a short answer
  messages,
});

// Use concise system prompts
system: 'Reply in 1-2 sentences.' // Not a 500-word personality description
```

### Step 5: Monitor Usage

```typescript
// Log every call's cost
function logUsage(message: Anthropic.Message) {
  const { input_tokens, output_tokens } = message.usage;
  const cost = (input_tokens * 3 + output_tokens * 15) / 1_000_000; // Sonnet pricing
  console.log(`Tokens: ${input_tokens}in/${output_tokens}out | Cost: $${cost.toFixed(4)}`);
}
```

## Cost Comparison Example

Processing 10,000 documents (avg 500 tokens each, 200 token response):

| Strategy | Input Cost | Output Cost | Total |
|----------|-----------|-------------|-------|
| Opus, no optimization | $75.00 | $150.00 | $225.00 |
| Sonnet, no optimization | $15.00 | $30.00 | $45.00 |
| Sonnet + Batches | $7.50 | $15.00 | $22.50 |
| Haiku + Batches | $2.00 | $4.00 | $6.00 |
| Haiku + Batches + Caching | ~$1.00 | $4.00 | ~$5.00 |

## Output

- Model selection optimized per task complexity (Haiku for simple, Sonnet for balanced, Opus for complex)
- Prompt caching enabled for repeated system prompts
- Batch processing configured for non-urgent workloads
- Token usage logged with cost estimates per request
- Spending alerts configured in Anthropic console

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| API Error | Check error type and status code | See `clade-common-errors` |

## Examples

See Pricing table, five numbered strategy sections with code, and the Cost Comparison Example table showing savings from $225 to $5 for 10K documents.

## Resources

- [Pricing](https://www.anthropic.com/pricing)
- [Prompt Caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Message Batches](https://platform.claude.com/docs/en/api/messages/batches/create)
- [Token Counting](https://platform.claude.com/docs/en/api/messages/count_tokens)

## Next Steps

See `clade-performance-tuning` for latency optimization.

## Prerequisites

- Completed `clade-install-auth`
- Active API usage to optimize
- Access to Anthropic console for usage monitoring
