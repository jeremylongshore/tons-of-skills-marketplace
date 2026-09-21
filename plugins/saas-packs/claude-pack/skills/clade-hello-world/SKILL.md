---
name: clade-hello-world
description: 'Send your first message to Claude using the Anthropic SDK.

  Use when starting a new Claude integration, testing your setup,

  or learning the Messages API basics.

  Trigger with phrases like "anthropic hello world", "claude api example",

  "first claude call", "anthropic quick start".

  '
allowed-tools: Read, Write, Edit
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- messages-api
compatibility: Designed for Claude Code
---
# Anthropic Hello World

## Overview

Send your first message to Claude and get a response using the Messages API.

## Prerequisites

- Completed `clade-install-auth` setup
- `ANTHROPIC_API_KEY` environment variable set

## Instructions

### Step 1: Basic Message

```typescript
import Anthropic from '@claude-ai/sdk';

const client = new Anthropic();

const message = await client.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  messages: [
    { role: 'user', content: 'What is the capital of France?' }
  ],
});

console.log(message.content[0].text);
// "The capital of France is Paris."
```

### Step 2: Add a System Prompt

```typescript
const message = await client.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  system: 'You are a helpful geography expert. Be concise.',
  messages: [
    { role: 'user', content: 'What is the capital of France?' }
  ],
});
```

### Step 3: Multi-Turn Conversation

```typescript
const message = await client.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  messages: [
    { role: 'user', content: 'What is the capital of France?' },
    { role: 'assistant', content: 'The capital of France is Paris.' },
    { role: 'user', content: 'What is its population?' },
  ],
});
```

## Python Example

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ],
)
print(message.content[0].text)
```

## Output

- `message.content[0].text` — Claude's text response
- `message.model` — model ID used
- `message.usage.input_tokens` / `message.usage.output_tokens` — token counts
- `message.stop_reason` — `end_turn`, `max_tokens`, or `tool_use`

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `authentication_error` | Bad API key | Check `ANTHROPIC_API_KEY` |
| `invalid_request_error` | Missing required field | Both `messages` and `max_tokens` are required |
| `not_found_error` | Invalid model ID | Use a valid model like `claude-sonnet-4-20250514` |

## Available Models

| Model | Best For | Context | Cost (input/output per MTok) |
|-------|----------|---------|------------------------------|
| `claude-opus-4-20250514` | Complex reasoning | 200K | $15 / $75 |
| `claude-sonnet-4-20250514` | Balanced quality + speed | 200K | $3 / $15 |
| `claude-haiku-4-5-20251001` | Fast, cheap tasks | 200K | $0.80 / $4 |

## Examples

See Step 1 (basic message), Step 2 (system prompt), and Step 3 (multi-turn) above. Python example included in its own section.

## Resources

- [Messages API Reference](https://platform.claude.com/docs/en/api/messages)
- [Model Overview](https://platform.claude.com/docs/en/models/overview)

## Next Steps

Proceed to `clade-model-inference` for streaming and advanced patterns.
