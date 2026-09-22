---
name: clade-model-inference
description: 'Stream Claude responses, use system prompts, handle multi-turn conversations,

  Use when working with model-inference patterns.

  and process structured output with the Messages API.

  Trigger with "anthropic streaming", "claude messages api", "claude inference",

  "stream claude response".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- streaming
- messages-api
compatibility: Designed for Claude Code
---
# Anthropic Messages API — Streaming & Advanced Patterns

## Overview

The Messages API is the only inference endpoint. Every Claude interaction goes through `client.messages.create()`. This skill covers streaming, system prompts, vision, and structured output.

## Prerequisites

- Completed `clade-install-auth`
- Familiarity with `clade-hello-world`

## Instructions

### Step 1: Streaming Responses

```typescript
import Anthropic from '@claude-ai/sdk';

const client = new Anthropic();

const stream = client.messages.stream({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  messages: [{ role: 'user', content: 'Write a haiku about TypeScript.' }],
});

for await (const event of stream) {
  if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
    process.stdout.write(event.delta.text);
  }
}

const finalMessage = await stream.finalMessage();
console.log('\n\nTokens:', finalMessage.usage);
```

### Step 2: Vision — Sending Images

```typescript
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
          data: fs.readFileSync('screenshot.png').toString('base64'),
        },
      },
      { type: 'text', text: 'Describe what you see in this image.' },
    ],
  }],
});
```

### Step 3: JSON / Structured Output

```typescript
const message = await client.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  system: `Respond with valid JSON only. Schema: { "summary": string, "sentiment": "positive"|"negative"|"neutral", "confidence": number }`,
  messages: [{ role: 'user', content: 'Analyze: "This product exceeded my expectations!"' }],
});

const result = JSON.parse(message.content[0].text);
// { summary: "Very positive review", sentiment: "positive", confidence: 0.95 }
```

## Python Streaming

```python
import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a haiku about Python."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

print(f"\nTokens: {stream.get_final_message().usage}")
```

## Output

- **Non-streaming:** Full `Message` object with `content`, `usage`, `stop_reason`
- **Streaming events:**
  - `message_start` — message metadata
  - `content_block_start` — new content block beginning
  - `content_block_delta` — incremental text (`text_delta`) or tool input (`input_json_delta`)
  - `message_delta` — final `stop_reason` and usage
  - `message_stop` — stream complete

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `overloaded_error` (529) | Anthropic API temporarily overloaded | Retry with exponential backoff; use `client.messages.create` with built-in retries |
| `rate_limit_error` (429) | Exceeded RPM or TPM | Check `retry-after` header. See `clade-rate-limits` |
| `invalid_request_error` | Image too large or bad format | Max 20 images per request. Supported: PNG, JPEG, GIF, WebP. Max 5MB each |

## Key Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | string | Required. Model ID (e.g. `claude-sonnet-4-20250514`) |
| `max_tokens` | int | Required. Maximum output tokens (1–8192 typical) |
| `messages` | array | Required. Alternating user/assistant messages |
| `system` | string | Optional. System prompt for behavior/persona |
| `temperature` | float | Optional. 0.0–1.0, default 1.0 |
| `top_p` | float | Optional. Nucleus sampling threshold |
| `stop_sequences` | string[] | Optional. Custom stop strings |
| `stream` | boolean | Optional. Enable SSE streaming |

## Examples

See Step 1 (streaming), Step 2 (vision with base64 images), and Step 3 (structured JSON output) above. Python streaming example included.

## Resources

- [Messages API](https://platform.claude.com/docs/en/api/messages)
- [Streaming](https://platform.claude.com/docs/en/build-with-claude/streaming)
- [Vision](https://platform.claude.com/docs/en/build-with-claude/vision)

## Next Steps

See `clade-embeddings-search` for tool use and function calling patterns.
