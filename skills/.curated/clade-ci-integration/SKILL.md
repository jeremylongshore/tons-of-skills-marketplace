---
name: clade-ci-integration
description: "Test and validate Claude integrations in CI/CD pipelines \u2014\nUse\
  \ when working with ci-integration patterns.\nGitHub Actions, mocking strategies,\
  \ and cost control.\nTrigger with \"anthropic ci\", \"test claude in ci\", \"anthropic\
  \ github actions\",\n\"claude automated testing\".\n"
allowed-tools: Read, Write, Edit, Bash(npm:*)
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- ci
- testing
compatibility: Designed for Claude Code
---
# Anthropic CI Integration

## Overview

Testing Claude integrations in CI requires handling API keys securely, mocking for unit tests, and making real calls only in integration tests.

## GitHub Actions Setup

```yaml
# .github/workflows/test.yml
name: Test Claude Integration
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - run: npm ci

      # Unit tests — no API key needed (mocked)
      - run: npm run test:unit

      # Integration tests — real API calls
      - run: npm run test:integration
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Mock Strategy for Unit Tests

```typescript
// tests/helpers/mock-anthropic.ts
import { vi } from 'vitest';

export function mockAnthropicClient() {
  return {
    messages: {
      create: vi.fn().mockResolvedValue({
        id: 'msg_mock',
        type: 'message',
        role: 'assistant',
        model: 'claude-sonnet-4-20250514',
        content: [{ type: 'text', text: 'Mock response' }],
        stop_reason: 'end_turn',
        usage: { input_tokens: 10, output_tokens: 5 },
      }),
      stream: vi.fn().mockReturnValue({
        async *[Symbol.asyncIterator]() {
          yield { type: 'content_block_delta', delta: { type: 'text_delta', text: 'Mock' } };
        },
        finalMessage: vi.fn().mockResolvedValue({ usage: { input_tokens: 10, output_tokens: 5 } }),
      }),
    },
  };
}

// In your test:
import { mockAnthropicClient } from './helpers/mock-anthropic';

test('summarize function returns text', async () => {
  const client = mockAnthropicClient();
  const result = await summarize(client, 'Some long text...');
  expect(result).toBe('Mock response');
  expect(client.messages.create).toHaveBeenCalledWith(
    expect.objectContaining({ model: 'claude-sonnet-4-20250514' })
  );
});
```

## Integration Test (Real API)

```typescript
// tests/integration/claude.test.ts
import Anthropic from '@claude-ai/sdk';
import { describe, test, expect } from 'vitest';

describe('Claude API Integration', () => {
  const client = new Anthropic(); // Uses ANTHROPIC_API_KEY env var

  test('messages.create returns valid response', async () => {
    const message = await client.messages.create({
      model: 'claude-haiku-4-5-20251001', // Cheapest for CI
      max_tokens: 50,
      messages: [{ role: 'user', content: 'Say "test passed" in 2 words.' }],
    });

    expect(message.content[0].type).toBe('text');
    expect(message.stop_reason).toBe('end_turn');
    expect(message.usage.output_tokens).toBeGreaterThan(0);
  }, 30_000); // 30s timeout for API calls
});
```

## Cost Control in CI

| Strategy | How |
|----------|-----|
| Use Haiku only | Cheapest model, fast |
| Limit max_tokens | `max_tokens: 50` for validation tests |
| Skip on PRs from forks | Don't expose API key to untrusted code |
| Run integration tests only on main | `if: github.ref == 'refs/heads/main'` |
| Budget cap | Set spending limits in Anthropic console |

## Output

- GitHub Actions workflow running unit tests (mocked, no API key needed)
- Integration tests making real Claude API calls on main branch
- Mock client returning realistic response shapes for unit tests
- CI costs controlled via Haiku model and tight max_tokens

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| API Error | Check error type and status code | See `clade-common-errors` |

## Examples

See GitHub Actions YAML, Mock Strategy with Vitest, Integration Test with real API, and Cost Control table above.

## Resources

- GitHub Actions Secrets
- Anthropic SDK

## Next Steps

See `clade-deploy-integration` for deploying to production.

## Prerequisites

- GitHub repository with Actions enabled
- `ANTHROPIC_API_KEY` stored as GitHub Actions secret
- Test framework installed (Vitest, Jest, or pytest)

## Instructions

### Step 1: Review the patterns below

Each section contains production-ready code examples. Copy and adapt them to your use case.

### Step 2: Apply to your codebase

Integrate the patterns that match your requirements. Test each change individually.

### Step 3: Verify

Run your test suite to confirm the integration works correctly.
