---
name: anth-install-auth
description: 'Install and configure Anthropic Claude SDK authentication for Python
  and TypeScript.

  Use when setting up a new Claude API integration, configuring API keys,

  or initializing the Anthropic SDK in your project.

  Trigger with phrases like "install anthropic", "setup claude api",

  "anthropic auth", "configure anthropic API key", "claude sdk setup".

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
# Anthropic Install & Auth

## Overview

Set up the official Anthropic SDK for Python or TypeScript and configure API key authentication. The SDK wraps the Claude Messages API at `https://api.anthropic.com/v1/messages`.

## Prerequisites

- Node.js 18+ or Python 3.8+
- Package manager (npm, pnpm, yarn, or pip)
- Anthropic account with API access at [console.anthropic.com](https://console.anthropic.com)
- API key from Console > API Keys

## Instructions

### Step 1: Install SDK

```bash
# Python
pip install anthropic

# TypeScript / Node.js
npm install @anthropic-ai/sdk

# With pnpm
pnpm add @anthropic-ai/sdk
```

### Step 2: Configure API Key

```bash
# Set environment variable (recommended)
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Or add to .env file
echo 'ANTHROPIC_API_KEY=sk-ant-api03-your-key-here' >> .env

# Verify it's set
echo $ANTHROPIC_API_KEY | head -c 15
# Expected: sk-ant-api03-...
```

### Step 3: Verify Connection (Python)

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=64,
    messages=[{"role": "user", "content": "Say hello in exactly 5 words."}]
)
print(message.content[0].text)
print(f"Model: {message.model}, Tokens: {message.usage.input_tokens}+{message.usage.output_tokens}")
```

### Step 4: Verify Connection (TypeScript)

```typescript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();  // reads ANTHROPIC_API_KEY from env

const message = await client.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 64,
  messages: [{ role: 'user', content: 'Say hello in exactly 5 words.' }],
});

if (message.content[0].type === 'text') {
  console.log(message.content[0].text);
}
console.log(`Stop reason: ${message.stop_reason}`);
```

## Output

- Installed SDK package (`anthropic` for Python, `@anthropic-ai/sdk` for TS)
- Environment variable `ANTHROPIC_API_KEY` configured
- Successful API response confirming authentication works

## Examples

For local Python development, install `anthropic` in the project virtual
environment, export `ANTHROPIC_API_KEY` only in the current shell, then run the
Step 3 script. Its successful text response confirms both package resolution
and authentication without adding a secret to the repository. For a Node
service, set the same variable in the deployment platform's secret manager and
run the TypeScript check once in a non-production environment; keep the key out
of source, logs, and client-side bundles.

## Error Handling

| Error | HTTP Code | Cause | Solution |
|-------|-----------|-------|----------|
| `authentication_error` | 401 | Invalid or missing API key | Verify key starts with `sk-ant-api03-` |
| `permission_error` | 403 | Key lacks required scope | Generate new key in Console |
| `not_found_error` | 404 | Invalid API endpoint | Ensure SDK is latest version |
| `ModuleNotFoundError` | N/A | SDK not installed | Run `pip install anthropic` or `npm install @anthropic-ai/sdk` |
| `connection_error` | N/A | Network/firewall blocking | Ensure HTTPS to `api.anthropic.com` is allowed |

## Enterprise Configuration

```python
# Custom base URL (for proxied environments)
client = anthropic.Anthropic(
    api_key="sk-ant-...",
    base_url="https://your-proxy.internal.com/v1",
    timeout=60.0,
    max_retries=3
)

# With explicit headers
client = anthropic.Anthropic(
    default_headers={"anthropic-beta": "messages-2024-12-19"}
)
```

## Security Considerations

- Never commit API keys to source control
- Use `.env` files with `.gitignore` exclusion
- Rotate keys periodically via Console > API Keys
- Use separate keys per environment (dev/staging/prod)
- Consider Anthropic's Workspace feature for team key isolation

## Resources

- [Anthropic API Getting Started](https://platform.claude.com/docs/en/api/overview)
- [Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- [TypeScript SDK](https://github.com/anthropics/anthropic-sdk-typescript)
- [Console](https://console.anthropic.com)

## Next Steps

After successful auth, proceed to `anth-hello-world` for your first Messages API call.
