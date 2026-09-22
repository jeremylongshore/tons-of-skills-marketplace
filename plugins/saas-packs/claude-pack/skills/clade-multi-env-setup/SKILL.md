---
name: clade-multi-env-setup
description: 'Configure Claude across dev, staging, and production with different

  Use when working with multi-env-setup patterns.

  models, keys, and rate limits per environment.

  Trigger with "anthropic environments", "claude staging",

  "anthropic dev vs prod", "claude multi-environment".

  '
allowed-tools: Read, Write, Edit
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- environments
- config
compatibility: Designed for Claude Code
---
# Anthropic Multi-Environment Setup

## Overview

Use different API keys, models, and limits across dev/staging/prod.

## Environment Configuration

```typescript
// config/anthropic.ts
interface AnthropicConfig {
  apiKey: string;
  model: string;
  maxTokens: number;
  maxRetries: number;
}

const configs: Record<string, AnthropicConfig> = {
  development: {
    apiKey: process.env.ANTHROPIC_API_KEY!,
    model: 'claude-haiku-4-5-20251001', // Cheap for dev
    maxTokens: 256,
    maxRetries: 1,
  },
  staging: {
    apiKey: process.env.ANTHROPIC_API_KEY!,
    model: 'claude-sonnet-4-20250514',
    maxTokens: 1024,
    maxRetries: 2,
  },
  production: {
    apiKey: process.env.ANTHROPIC_API_KEY!,
    model: 'claude-sonnet-4-20250514',
    maxTokens: 4096,
    maxRetries: 3,
  },
};

export const config = configs[process.env.NODE_ENV || 'development'];
```

## Separate API Keys Per Environment

Use different Anthropic API keys for each environment:

- **Dev key**: Low tier, spending alerts at $10
- **Staging key**: Medium tier, spending alerts at $50
- **Prod key**: Highest tier, spending alerts at usage baseline + 50%

```bash
# .env.development
ANTHROPIC_API_KEY=sk-ant-dev-...

# .env.staging
ANTHROPIC_API_KEY=sk-ant-staging-...

# .env.production
ANTHROPIC_API_KEY=sk-ant-prod-...
```

## Model Selection Strategy

| Environment | Model | Why |
|-------------|-------|-----|
| Development | Haiku | Fast iteration, cheap |
| Staging | Sonnet | Match prod quality |
| Production | Sonnet (default) | Balanced cost/quality |
| Production (complex) | Opus | Complex reasoning tasks |

## Output

- Environment-specific Anthropic configuration (model, maxTokens, maxRetries)
- Separate API keys per environment with appropriate tier limits
- Spending alerts configured per environment
- Dev using Haiku (cheap), staging matching prod (Sonnet), prod using Sonnet/Opus

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| API Error | Check error type and status code | See `clade-common-errors` |

## Examples

See Environment Configuration TypeScript pattern, API key separation strategy, and Model Selection Strategy table above.

## Resources

- [API Key Management](https://console.anthropic.com/settings/keys)

## Next Steps

See `clade-observability` for monitoring across environments.

## Prerequisites

- Completed `clade-install-auth`
- Multiple environments (dev/staging/prod) configured
- Separate Anthropic API keys created per environment

## Instructions

### Step 1: Review the patterns below

Each section contains production-ready code examples. Copy and adapt them to your use case.

### Step 2: Apply to your codebase

Integrate the patterns that match your requirements. Test each change individually.

### Step 3: Verify

Run your test suite to confirm the integration works correctly.
