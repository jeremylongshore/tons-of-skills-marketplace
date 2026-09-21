---
name: clade-sdk-patterns
description: "Production-ready Anthropic SDK patterns \u2014 client config, retries,\
  \ timeouts,\nUse when working with sdk-patterns patterns.\nerror handling, TypeScript\
  \ types, and async patterns.\nTrigger with \"anthropic sdk\", \"claude client setup\"\
  , \"anthropic typescript\",\n\"anthropic python patterns\".\n"
allowed-tools: Read, Write, Edit
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- sdk
- typescript
- python
compatibility: Designed for Claude Code
---
# Anthropic SDK Patterns

## Overview

Production patterns for the `@claude-ai/sdk` (TypeScript) and `anthropic` (Python) SDKs.

## Client Configuration

## Instructions

### Step 1: TypeScript

```typescript
import Anthropic from '@claude-ai/sdk';

// Default — reads ANTHROPIC_API_KEY from env
const client = new Anthropic();

// Full configuration
const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,   // default: env var
  maxRetries: 3,                            // default: 2
  timeout: 60_000,                          // default: 10 minutes
  baseURL: 'https://api.anthropic.com',     // override for proxies
  defaultHeaders: {                         // custom headers
    'claude-beta': 'prompt-caching-2024-07-31',
  },
});
```

### Step 2: Python

```python
import anthropic

# Sync client
client = anthropic.Anthropic()

# Async client
client = anthropic.AsyncAnthropic()

# Full configuration
client = anthropic.Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"],
    max_retries=3,
    timeout=60.0,
    base_url="https://api.anthropic.com",
    default_headers={"claude-beta": "prompt-caching-2024-07-31"},
)
```

## Output

- Properly configured client with retries, timeouts, and custom headers
- Type-safe error handling with specific exception classes
- Streaming implementation using your preferred pattern
- Prompt caching enabled for repeated system prompts (90% cost savings)
- Batch processing configured for bulk operations (50% cost savings)

## Error Handling

```typescript
import Anthropic from '@claude-ai/sdk';

try {
  const message = await client.messages.create({ ... });
} catch (err) {
  if (err instanceof Anthropic.AuthenticationError) {
    // 401 — bad API key
  } else if (err instanceof Anthropic.RateLimitError) {
    // 429 — back off and retry
  } else if (err instanceof Anthropic.APIError) {
    // All other API errors
    console.error(err.status, err.error?.type, err.message);
  } else if (err instanceof Anthropic.APIConnectionError) {
    // Network failure — DNS, timeout, etc.
  }
}
```

```python
try:
    message = client.messages.create(...)
except anthropic.AuthenticationError:
    ...  # 401
except anthropic.RateLimitError:
    ...  # 429
except anthropic.APIStatusError as e:
    print(e.status_code, e.message)
except anthropic.APIConnectionError:
    ...  # network failure
```

## Streaming Patterns

### Event-Based (TypeScript)

```typescript
const stream = client.messages.stream({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 2048,
  messages,
});

stream.on('text', (text) => process.stdout.write(text));
stream.on('error', (err) => console.error('Stream error:', err));
stream.on('end', () => console.log('\nDone'));

const finalMessage = await stream.finalMessage();
```

### Async Iterator (TypeScript)

```typescript
const stream = await client.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 2048,
  messages,
  stream: true,
});

for await (const event of stream) {
  if (event.type === 'content_block_delta') {
    process.stdout.write(event.delta.text || '');
  }
}
```

### Context Manager (Python)

```python
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,
    messages=messages,
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

message = stream.get_final_message()
```

## TypeScript Types

```typescript
import Anthropic from '@claude-ai/sdk';

// Message types
type Message = Anthropic.Message;
type MessageParam = Anthropic.MessageParam;
type ContentBlock = Anthropic.ContentBlock;
type TextBlock = Anthropic.TextBlock;
type ToolUseBlock = Anthropic.ToolUseBlock;

// Tool types
type Tool = Anthropic.Tool;
type ToolResultBlockParam = Anthropic.ToolResultBlockParam;

// Request/response
type MessageCreateParams = Anthropic.MessageCreateParams;
```

## Prompt Caching (Beta)

```typescript
const message = await client.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  system: [
    {
      type: 'text',
      text: longSystemPrompt, // 1024+ tokens to be cacheable
      cache_control: { type: 'ephemeral' },
    },
  ],
  messages: [{ role: 'user', content: userQuestion }],
}, {
  headers: { 'claude-beta': 'prompt-caching-2024-07-31' },
});
// Cache hit: 90% cheaper on input tokens
// message.usage.cache_creation_input_tokens / cache_read_input_tokens
```

## Message Batches

```typescript
// Submit up to 10,000 messages as a batch (50% cheaper, 24h SLA)
const batch = await client.messages.batches.create({
  requests: items.map((item, i) => ({
    custom_id: `item-${i}`,
    params: {
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1024,
      messages: [{ role: 'user', content: item.prompt }],
    },
  })),
});

// Poll for completion
let status = await client.messages.batches.retrieve(batch.id);
while (status.processing_status !== 'ended') {
  await new Promise(r => setTimeout(r, 30000));
  status = await client.messages.batches.retrieve(batch.id);
}
```

## Examples

See Client Configuration, Error Handling, Streaming Patterns, TypeScript Types, Prompt Caching, and Message Batches sections above for complete code examples.

## Resources

- TypeScript SDK
- Python SDK
- [Prompt Caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Message Batches](https://platform.claude.com/docs/en/api/messages/batches/create)

## Next Steps

See `clade-rate-limits` for throughput optimization.

## Prerequisites

- Completed `clade-install-auth`
- Familiarity with TypeScript generics or Python type hints
- Understanding of async/await patterns
