---
name: clade-install-auth
description: 'Install and configure the Anthropic SDK for Claude API access.

  Use when setting up Claude integration, configuring API keys,

  or initializing the Anthropic client in your project.

  Trigger with phrases like "install anthropic", "setup claude api",

  "anthropic auth", "configure anthropic API key".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(pip:*), Grep
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- ai
compatibility: Designed for Claude Code
---
# Anthropic Install & Auth

## Overview

Set up the Anthropic SDK and configure your API key to start using Claude models.

## Prerequisites

- Node.js 18+ or Python 3.10+
- Anthropic account at [console.anthropic.com](https://console.anthropic.com)
- API key from Settings → API Keys (starts with `sk-ant-`)

## Instructions

### Step 1: Install SDK

```bash
# Node.js / TypeScript
npm install @claude-ai/sdk

# Python
pip install anthropic
```

### Step 2: Configure API Key

```bash
# Set environment variable (recommended)
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Or add to .env file
echo 'ANTHROPIC_API_KEY=sk-ant-api03-...' >> .env
```

> **Important:** Never hardcode API keys. Use environment variables or a secrets manager. Keys start with `sk-ant-`.

### Step 3: Verify Connection

```typescript
import Anthropic from '@claude-ai/sdk';

const client = new Anthropic(); // reads ANTHROPIC_API_KEY from env

const message = await client.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 64,
  messages: [{ role: 'user', content: 'Say "connected" in one word.' }],
});
console.log(message.content[0].text); // "Connected"
```

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=64,
    messages=[{"role": "user", "content": "Say 'connected' in one word."}],
)
print(message.content[0].text)  # "Connected"
```

## Output

- `@claude-ai/sdk` in node_modules or `anthropic` in site-packages
- `ANTHROPIC_API_KEY` environment variable set
- Successful Claude response confirming API access

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `authentication_error` (401) | API key missing, invalid, or revoked | Check key at console.anthropic.com → API Keys |
| `permission_error` (403) | Key lacks access to requested model | Verify workspace has model access enabled |
| `ModuleNotFoundError` | SDK not installed | `pip install anthropic` or `npm i @claude-ai/sdk` |
| `Could not resolve host` | Network/DNS issue | Check internet connectivity and proxy settings |

## Examples

### TypeScript Setup

```typescript
import Anthropic from '@claude-ai/sdk';

// Default: reads ANTHROPIC_API_KEY from environment
const client = new Anthropic();

// Explicit key (for testing only — don't hardcode in production)
const client = new Anthropic({ apiKey: 'sk-ant-api03-...' });

// Custom base URL (for proxies or Vertex AI)
const client = new Anthropic({
  baseURL: 'https://your-proxy.example.com',
});
```

### Python Setup

```python
import anthropic

# Default: reads ANTHROPIC_API_KEY from environment
client = anthropic.Anthropic()

# Explicit key
client = anthropic.Anthropic(api_key="sk-ant-api03-...")

# Async client
client = anthropic.AsyncAnthropic()
```

## Resources

- [Anthropic API Docs](https://platform.claude.com/docs/en/api/overview)
- [Console Dashboard](https://console.anthropic.com)
- [API Key Management](https://console.anthropic.com/settings/keys)
- [Anthropic Status](https://status.anthropic.com)

## Next Steps

After successful auth, proceed to `clade-hello-world` for your first Claude conversation.
