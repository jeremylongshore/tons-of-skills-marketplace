---
name: anth-sdk-patterns
description: 'Apply production-ready Anthropic SDK patterns for TypeScript and Python.

  Use when implementing Claude integrations, building reusable wrappers,

  or establishing team coding standards for the Messages API.

  Trigger with phrases like "anthropic SDK patterns", "claude best practices",

  "anthropic code patterns", "production claude code".

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
# Anthropic SDK Patterns

## Overview

Production-ready patterns for the Anthropic SDK covering client management, error handling, type safety, and multi-tenant configurations.

## Prerequisites

- Completed `anth-install-auth` setup
- Familiarity with async/await patterns
- TypeScript 5+ or Python 3.10+

## Pattern 1: Typed Wrapper with Retry

```typescript
import Anthropic from '@anthropic-ai/sdk';
import type { Message, MessageCreateParams } from '@anthropic-ai/sdk/resources/messages';

class ClaudeService {
  private client: Anthropic;

  constructor(apiKey?: string) {
    this.client = new Anthropic({
      apiKey: apiKey || process.env.ANTHROPIC_API_KEY,
      maxRetries: 3,      // SDK handles 429 + 5xx automatically
      timeout: 60_000,
    });
  }

  async complete(
    prompt: string,
    options: Partial<MessageCreateParams> = {}
  ): Promise<string> {
    const message = await this.client.messages.create({
      model: options.model || 'claude-sonnet-4-20250514',
      max_tokens: options.max_tokens || 1024,
      messages: [{ role: 'user', content: prompt }],
      ...options,
    });

    const textBlock = message.content.find((b) => b.type === 'text');
    if (!textBlock || textBlock.type !== 'text') {
      throw new Error(`No text in response: ${message.stop_reason}`);
    }
    return textBlock.text;
  }

  async *stream(prompt: string, model = 'claude-sonnet-4-20250514'): AsyncGenerator<string> {
    const stream = this.client.messages.stream({
      model,
      max_tokens: 4096,
      messages: [{ role: 'user', content: prompt }],
    });

    for await (const event of stream) {
      if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
        yield event.delta.text;
      }
    }
  }
}
```

## Pattern 2: Multi-Turn Conversation Manager

```python
import anthropic
from dataclasses import dataclass, field

@dataclass
class Conversation:
    client: anthropic.Anthropic = field(default_factory=anthropic.Anthropic)
    model: str = "claude-sonnet-4-20250514"
    system: str = ""
    messages: list = field(default_factory=list)
    max_tokens: int = 4096

    def say(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.system,
            messages=self.messages,
        )

        assistant_text = response.content[0].text
        self.messages.append({"role": "assistant", "content": assistant_text})
        return assistant_text

    @property
    def token_count(self) -> int:
        """Estimate total tokens in conversation."""
        return sum(len(str(m["content"])) // 4 for m in self.messages)

# Usage
conv = Conversation(system="You are a helpful coding assistant.")
print(conv.say("What is a closure in JavaScript?"))
print(conv.say("Can you show me an example?"))  # Has full context
```

## Pattern 3: Structured Output with Prefill

```python
import json
import anthropic

client = anthropic.Anthropic()

def extract_structured(text: str, schema_description: str) -> dict:
    """Force JSON output using assistant prefill technique."""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": f"Extract data from this text as JSON.\n\nSchema: {schema_description}\n\nText: {text}"},
            {"role": "assistant", "content": "{"}  # Prefill forces JSON output
        ]
    )
    json_str = "{" + message.content[0].text
    return json.loads(json_str)

# Usage
data = extract_structured(
    "John Smith, 35, lives in NYC and works at Google as a PM.",
    '{"name": str, "age": int, "city": str, "company": str, "role": str}'
)
# {"name": "John Smith", "age": 35, "city": "NYC", "company": "Google", "role": "PM"}
```

## Pattern 4: Multi-Tenant Client Factory

```typescript
const clients = new Map<string, Anthropic>();

export function getClientForTenant(tenantId: string): Anthropic {
  if (!clients.has(tenantId)) {
    const apiKey = getApiKeyForTenant(tenantId);  // From your secret store
    clients.set(tenantId, new Anthropic({ apiKey }));
  }
  return clients.get(tenantId)!;
}
```

## Pattern 5: Token-Aware Request Sizing

```python
# Use the Token Counting API to pre-check request size
count = client.messages.count_tokens(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": long_document}],
    system="You are a summarizer."
)
print(f"Input will use {count.input_tokens} tokens")

# Adjust max_tokens to stay within budget
remaining_budget = 200_000 - count.input_tokens
max_tokens = min(4096, remaining_budget)
```

## Instructions

Choose one pattern for the integration boundary instead of copying all of them
into a single client. Start with the typed wrapper for a service that returns
text, add the conversation manager only when the application owns turn history,
and use token counting before submitting large documents. Keep tenant keys in a
server-side secret store and make the factory key its cache by tenant identity;
never accept or persist a customer key in browser code. Test the selected
wrapper with a mocked SDK response before enabling live requests.

## Output

The selected pattern yields a stable application-level interface: a text value
or stream for an interactive request, a JSON object that has passed parsing for
structured extraction, or a tenant-scoped client whose credentials remain
isolated. Failures are surfaced as explicit SDK errors or a missing-text/JSON
parsing error rather than silently returning partial data.

## Examples

For a support API, instantiate one `ClaudeService` at process startup and call
`complete()` from the server route; return its string only after the wrapper has
confirmed a text block. For a document import, call `count_tokens()` first,
reduce the requested output to the remaining budget, then pass the bounded
request to the wrapper. In a multi-tenant service, resolve the tenant's key
from the secret store and use `getClientForTenant()` so one customer's retry or
usage state cannot be confused with another's.

## Error Handling

| Pattern | Use Case | Benefit |
|---------|----------|---------|
| SDK `maxRetries` | 429 / 5xx errors | Built-in exponential backoff |
| Prefill technique | Force JSON output | No regex parsing needed |
| Token counting | Long documents | Prevent context overflow |
| Client factory | Multi-tenant SaaS | Key isolation per customer |

## Resources

- [Client SDKs](https://platform.claude.com/docs/en/cli-sdks-libraries/overview)
- [Token Counting API](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- [Prompt Caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)

## Next Steps

Apply patterns in `anth-core-workflow-a` for tool use workflows.
