---
name: clade-local-dev-loop
description: "Set up a fast local development loop for building with the Anthropic\
  \ API \u2014\nUse when working with local-dev-loop patterns.\nhot reload, cost-saving\
  \ tips, and test patterns.\nTrigger with \"anthropic dev setup\", \"claude local\
  \ development\",\n\"anthropic test locally\", \"claude dev workflow\".\n"
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(pip:*)
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- development
- testing
compatibility: Designed for Claude Code
---
# Anthropic Local Dev Loop

## Overview

Set up a fast, cheap development workflow for building with Claude.

## Prerequisites

- Node.js 18+ or Python 3.10+
- `ANTHROPIC_API_KEY` environment variable set
- npm or pip package manager

## Instructions

### Step 1: Project Setup

```bash
mkdir my-claude-app && cd my-claude-app
npm init -y
npm install @claude-ai/sdk dotenv tsx

# Create .env (never commit this)
echo 'ANTHROPIC_API_KEY=sk-ant-api03-...' > .env
echo '.env' >> .gitignore
```

### Step 2: Create a Test Script

```typescript
// src/test-prompt.ts
import 'dotenv/config';
import Anthropic from '@claude-ai/sdk';

const client = new Anthropic();

async function main() {
  const message = await client.messages.create({
    model: 'claude-haiku-4-5-20251001', // Use Haiku for dev — 20x cheaper than Opus
    max_tokens: 512,
    messages: [{ role: 'user', content: 'Summarize this in one sentence: ...' }],
  });

  console.log(message.content[0].text);
  console.log(`Cost: ~$${((message.usage.input_tokens * 0.80 + message.usage.output_tokens * 4) / 1_000_000).toFixed(4)}`);
}

main();
```

### Step 3: Run with Hot Reload

```bash
# Watch mode — re-runs on file changes
npx tsx watch src/test-prompt.ts

# Or one-shot
npx tsx src/test-prompt.ts
```

## Cost-Saving Dev Tips

| Tip | Savings |
|-----|---------|
| Use `claude-haiku-4-5-20251001` during development | 20x cheaper than Opus |
| Set `max_tokens: 256` for testing | Fewer output tokens billed |
| Cache your system prompt with prompt caching beta | 90% off cached input tokens |
| Use Message Batches for bulk testing (50% off) | Half price, 24h turnaround |
| Log responses locally so you don't re-call for the same input | 100% savings on repeats |

## Mock Client for Unit Tests

```typescript
// tests/mock-anthropic.ts
export function createMockClient() {
  return {
    messages: {
      create: async (params: any) => ({
        id: 'msg_test',
        type: 'message',
        role: 'assistant',
        model: params.model,
        content: [{ type: 'text', text: 'Mock response for testing' }],
        stop_reason: 'end_turn',
        usage: { input_tokens: 10, output_tokens: 5 },
      }),
    },
  };
}

// In your test:
import { createMockClient } from './mock-anthropic';
const client = process.env.MOCK ? createMockClient() : new Anthropic();
```

## Python Dev Loop

```text
pip install anthropic python-dotenv ipython

# Interactive exploration
ANTHROPIC_API_KEY=sk-ant-... ipython
>>> import anthropic
>>> c = anthropic.Anthropic()
>>> r = c.messages.create(model="claude-haiku-4-5-20251001", max_tokens=100, messages=[{"role":"user","content":"hello"}])
>>> r.content[0].text
```

## Output

- Project scaffolded with SDK, dotenv, and tsx for hot reload
- Test script running against Claude Haiku (cheapest model)
- Mock client available for unit tests without API calls
- Cost estimate printed per request

## Error Handling

| Issue | Fix |
|-------|-----|
| `ANTHROPIC_API_KEY` not loading | Make sure `dotenv/config` is imported first |
| Slow iteration | Use Haiku, reduce max_tokens |
| High dev costs | Log responses, use mocks for unit tests |

## Examples

See Step 1 (project setup), Step 2 (test script with cost tracking), Step 3 (hot reload), Mock Client section, and Python Dev Loop section above.

## Resources

- [Quickstart Guide](https://platform.claude.com/docs/en/get-started)
- TypeScript SDK

## Next Steps

See `clade-sdk-patterns` for production client configuration.
