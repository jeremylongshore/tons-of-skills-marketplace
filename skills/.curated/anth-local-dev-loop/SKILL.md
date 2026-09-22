---
name: anth-local-dev-loop
description: 'Configure a local development workflow for Anthropic Claude API projects.

  Use when setting up dev environment, configuring hot reload,

  or establishing a fast iteration cycle with the Messages API.

  Trigger with phrases like "anthropic local dev", "claude dev setup",

  "anthropic development workflow", "test claude locally".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(pip:*), Grep
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- ai
- anthropic
compatibility: Designed for Claude Code
---
# Anthropic Local Dev Loop

## Overview

Set up a fast local development cycle for Claude API projects with environment management, request logging, cost tracking, and hot-reload.

## Prerequisites

- Completed `anth-install-auth` setup
- Node.js 18+ or Python 3.8+
- `.env` file with `ANTHROPIC_API_KEY`

## Instructions

### Step 1: Project Structure

```
my-claude-app/
├── .env                  # ANTHROPIC_API_KEY=sk-ant-...
├── .env.example          # ANTHROPIC_API_KEY=your-key-here
├── .gitignore            # Include .env
├── src/
│   ├── client.ts         # Singleton client
│   ├── prompts/          # System prompts as files
│   └── tools/            # Tool definitions
├── tests/
│   └── mock-responses/   # Saved API responses for testing
└── scripts/
    └── dev.ts            # Dev runner with logging
```

### Step 2: Singleton Client with Request Logging

```typescript
// src/client.ts
import Anthropic from '@anthropic-ai/sdk';

let client: Anthropic | null = null;

export function getClient(): Anthropic {
  if (!client) {
    client = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
      maxRetries: 2,
      timeout: 30_000,
    });
  }
  return client;
}

// Development logger — tracks cost per request
export function logUsage(messageId: string, usage: { input_tokens: number; output_tokens: number }, model: string) {
  const pricing: Record<string, { input: number; output: number }> = {
    'claude-sonnet-4-20250514': { input: 3.0, output: 15.0 },
    'claude-haiku-4-20250514': { input: 0.80, output: 4.0 },
    'claude-opus-4-20250514': { input: 15.0, output: 75.0 },
  };
  const rates = pricing[model] || pricing['claude-sonnet-4-20250514'];
  const cost = (usage.input_tokens * rates.input + usage.output_tokens * rates.output) / 1_000_000;
  console.log(`[${messageId}] ${model} | ${usage.input_tokens}+${usage.output_tokens} tokens | $${cost.toFixed(4)}`);
}
```

### Step 3: Mock Responses for Tests

```typescript
// tests/mock-client.ts
import { type Message } from '@anthropic-ai/sdk/resources/messages';

export function mockMessage(text: string): Message {
  return {
    id: 'msg_test_123',
    type: 'message',
    role: 'assistant',
    model: 'claude-sonnet-4-20250514',
    content: [{ type: 'text', text }],
    stop_reason: 'end_turn',
    stop_sequence: null,
    usage: { input_tokens: 10, output_tokens: 20 },
  };
}
```

### Step 4: Hot-Reload Dev Script

```text
# package.json scripts
"scripts": {
  "dev": "tsx watch src/index.ts",
  "dev:debug": "ANTHROPIC_LOG=debug tsx watch src/index.ts",
  "test": "vitest",
  "test:live": "LIVE_API=1 vitest --run"
}
```

## Output

The development loop produces a repeatable local project layout, a single
configured client, mock-backed tests, and a request log that records model and
token usage. A change can then be exercised with no API spend in the normal
test suite or with deliberately enabled live traffic when investigating a
prompt or integration behavior.

## Examples

While editing a prompt, run the default `vitest` command against a saved mock
response and confirm the application handles the expected text and stop reason.
When a real API check is needed, set `LIVE_API=1` only for that invocation,
choose the lower-cost development model, and inspect the logger for token use.
If the live response changes the contract, first update the fixture and its
assertions, then rerun the mock suite so later local iterations remain fast and
deterministic.

## Environment Management

```bash
# .env.example (commit this)
ANTHROPIC_API_KEY=your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514
ANTHROPIC_MAX_TOKENS=1024
ANTHROPIC_LOG=warn     # debug | info | warn | error

# Enable SDK debug logging
export ANTHROPIC_LOG=debug  # Logs all requests/responses
```

## Cost Control During Development

```python
import os

DEV_MODEL = "claude-haiku-4-20250514"      # $0.80/$4.00 per MTok
PROD_MODEL = "claude-sonnet-4-20250514"    # $3.00/$15.00 per MTok

model = DEV_MODEL if os.getenv("ENV") == "development" else PROD_MODEL
```

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Hot reload triggers duplicate requests | File save causes restart | Add debounce or save-on-explicit-action |
| `.env` not loading | Missing dotenv setup | Use `dotenv` package or `tsx --env-file=.env` |
| Mock tests pass but live fails | Response shape changed | Update mocks from real API responses |

## Resources

- [SDK Debug Logging](https://github.com/anthropics/anthropic-sdk-python#logging)
- [Pricing](https://platform.claude.com/docs/en/about-claude/pricing)

## Next Steps

Apply patterns in `anth-sdk-patterns` for production-ready code.
