---
name: anth-hello-world
description: 'Create a minimal working Anthropic Claude Messages API example.

  Use when starting a new Claude integration, testing your setup,

  or learning basic Messages API patterns for text, vision, and streaming.

  Trigger with phrases like "anthropic hello world", "claude api example",

  "anthropic quick start", "simple claude code", "first messages api call".

  '
allowed-tools: Read, Write, Edit
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- ai
- anthropic
compatibility: Designed for Claude Code
---
# Anthropic Hello World

## Overview

Three minimal examples covering the Claude Messages API core surfaces: basic text completion, vision (image analysis), and streaming responses.

## Prerequisites

- Completed `anth-install-auth` setup
- Valid `ANTHROPIC_API_KEY` in environment
- Python 3.8+ with `anthropic` package or Node.js 18+ with `@anthropic-ai/sdk`

## Instructions

### Example 1: Basic Text Message (Python)

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Explain quantum computing in 3 sentences."}
    ]
)

# Response structure
print(message.content[0].text)       # The actual text response
print(f"ID: {message.id}")           # msg_01XFDUDYJgAACzvnptvVoYEL
print(f"Model: {message.model}")     # claude-sonnet-4-20250514
print(f"Stop: {message.stop_reason}")# end_turn
print(f"Usage: {message.usage.input_tokens}in / {message.usage.output_tokens}out")
```

### Example 2: Vision — Analyze an Image (TypeScript)

```typescript
import Anthropic from '@anthropic-ai/sdk';
import * as fs from 'fs';

const client = new Anthropic();

// From file (base64)
const imageData = fs.readFileSync('chart.png').toString('base64');

const message = await client.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  messages: [{
    role: 'user',
    content: [
      {
        type: 'image',
        source: {
          type: 'base64',
          media_type: 'image/png',
          data: imageData,
        },
      },
      { type: 'text', text: 'Describe what this chart shows.' },
    ],
  }],
});

console.log(message.content[0].type === 'text' ? message.content[0].text : '');
```

### Example 3: Streaming Response (Python)

```python
import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a haiku about APIs."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

# Get final message with full metadata
final = stream.get_final_message()
print(f"\nTokens used: {final.usage.input_tokens}+{final.usage.output_tokens}")
```

## Output

- Working code file with Claude client initialization
- Successful API response with text content
- Console output showing model response and usage metadata

## Examples

Use the text example first when verifying credentials: send a fixed, short
prompt and confirm that `message.content[0].text` is present before integrating
the client into application code. Use the vision example only after that check
passes and replace `chart.png` with a non-sensitive local fixture. For an
interactive command-line feature, use the streaming example so text is emitted
incrementally, then read the final message to capture token usage for logs or
cost controls.

## Error Handling

| Error | HTTP Code | Cause | Solution |
|-------|-----------|-------|----------|
| `authentication_error` | 401 | Invalid API key | Check `ANTHROPIC_API_KEY` |
| `invalid_request_error` | 400 | Bad params (e.g., empty messages) | Validate request body |
| `rate_limit_error` | 429 | Too many requests | Implement backoff (see `anth-rate-limits`) |
| `overloaded_error` | 529 | API temporarily overloaded | Retry after 30-60s |
| `api_error` | 500 | Server error | Retry with exponential backoff |

## Key API Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `model` | Yes | Model ID: `claude-sonnet-4-20250514`, `claude-haiku-4-20250514`, `claude-opus-4-20250514` |
| `max_tokens` | Yes | Maximum output tokens (model-dependent max) |
| `messages` | Yes | Array of `{role, content}` objects |
| `system` | No | System prompt (string or content blocks) |
| `temperature` | No | 0.0-1.0, default 1.0 |
| `top_p` | No | Nucleus sampling (use temperature OR top_p) |
| `stop_sequences` | No | Array of strings that stop generation |
| `stream` | No | Enable SSE streaming |

## Resources

- [Messages API Reference](https://platform.claude.com/docs/en/api/messages)
- [Messages Examples](https://platform.claude.com/docs/en/build-with-claude/working-with-messages)
- [Vision Guide](https://platform.claude.com/docs/en/build-with-claude/vision)

## Next Steps

Proceed to `anth-local-dev-loop` for development workflow setup.
