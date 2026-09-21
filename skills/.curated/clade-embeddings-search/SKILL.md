---
name: clade-embeddings-search
description: 'Implement tool use (function calling) with Claude to let it execute
  actions,

  Use when working with embeddings-search patterns.

  query databases, call APIs, and interact with external systems.

  Trigger with "anthropic tool use", "claude function calling", "claude tools",

  "anthropic structured output with tools".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- tool-use
- function-calling
compatibility: Designed for Claude Code
---
# Anthropic Tool Use (Function Calling)

## Overview

Tool use lets Claude call functions you define — query databases, hit APIs, read files, do math. Claude decides when to call a tool, you execute it, and feed the result back. This is how you build Claude-powered agents.

> **Note:** Anthropic does not offer an embeddings API. For embeddings + vector search, pair Claude with a dedicated embedding model (OpenAI, Cohere, or Voyage).

## Prerequisites

- Completed `clade-model-inference`
- Understanding of JSON Schema for tool definitions

## Instructions

### Step 1: Define Tools

```typescript
import Anthropic from '@claude-ai/sdk';

const client = new Anthropic();

const tools: Anthropic.Tool[] = [
  {
    name: 'get_weather',
    description: 'Get current weather for a city. Call this when the user asks about weather.',
    input_schema: {
      type: 'object',
      properties: {
        city: { type: 'string', description: 'City name, e.g. "San Francisco"' },
        unit: { type: 'string', enum: ['celsius', 'fahrenheit'], description: 'Temperature unit' },
      },
      required: ['city'],
    },
  },
];
```

### Step 2: Send Message with Tools

```typescript
const response = await client.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  tools,
  messages: [{ role: 'user', content: "What's the weather in San Francisco?" }],
});

// Claude responds with stop_reason: 'tool_use'
// response.content includes a tool_use block:
// { type: 'tool_use', id: 'toolu_01...', name: 'get_weather', input: { city: 'San Francisco' } }
```

### Step 3: Execute Tool and Return Result

```typescript
// Find the tool use block
const toolUse = response.content.find(block => block.type === 'tool_use');

// Execute your function
const weatherData = await fetchWeather(toolUse.input.city);

// Send result back to Claude
const finalResponse = await client.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  tools,
  messages: [
    { role: 'user', content: "What's the weather in San Francisco?" },
    { role: 'assistant', content: response.content },
    {
      role: 'user',
      content: [{
        type: 'tool_result',
        tool_use_id: toolUse.id,
        content: JSON.stringify(weatherData),
      }],
    },
  ],
});

console.log(finalResponse.content[0].text);
// "The weather in San Francisco is currently 65°F and partly cloudy."
```

## Python Example

```python
import anthropic

client = anthropic.Anthropic()

tools = [{
    "name": "get_weather",
    "description": "Get current weather for a city.",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string"},
        },
        "required": ["city"],
    },
}]

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "Weather in Paris?"}],
)

# Process tool_use blocks in response.content
for block in response.content:
    if block.type == "tool_use":
        result = execute_tool(block.name, block.input)
        # Send tool_result back...
```

## Agentic Tool Loop

```typescript
// Keep calling Claude until it stops requesting tools
let messages = [{ role: 'user', content: userInput }];

while (true) {
  const response = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 4096,
    tools,
    messages,
  });

  // Add assistant response to conversation
  messages.push({ role: 'assistant', content: response.content });

  if (response.stop_reason === 'end_turn') {
    // Claude is done — extract final text
    const text = response.content.find(b => b.type === 'text')?.text;
    console.log(text);
    break;
  }

  // Execute all tool calls and send results
  const toolResults = [];
  for (const block of response.content) {
    if (block.type === 'tool_use') {
      const result = await executeTool(block.name, block.input);
      toolResults.push({
        type: 'tool_result',
        tool_use_id: block.id,
        content: JSON.stringify(result),
      });
    }
  }
  messages.push({ role: 'user', content: toolResults });
}
```

## Output

- `tool_use` content blocks with `name` and `input` when Claude wants to call a tool
- `stop_reason: "tool_use"` indicating Claude is waiting for tool results
- Final text response after all tool results are provided
- Complete agentic loop until `stop_reason: "end_turn"`

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `invalid_request_error` | Bad tool schema | Validate JSON Schema. `input_schema` must be a valid JSON Schema object |
| `tool_use` with no matching name | Claude hallucinated a tool | Check `tool_use.name` against your defined tools before executing |
| `tool_result` mismatch | Wrong `tool_use_id` | Each `tool_result` must reference the exact `id` from the `tool_use` block |

## Examples

See Step 1 (tool definition), Step 2 (sending with tools), Step 3 (executing and returning results), and the full agentic tool loop example above.

## Resources

- [Tool Use Guide](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Tool Use API Reference](https://platform.claude.com/docs/en/api/messages)

## Next Steps

See `clade-common-errors` for error handling patterns.
