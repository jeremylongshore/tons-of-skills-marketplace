---
name: anth-core-workflow-a
description: 'Build Claude tool use (function calling) workflows with the Messages
  API.

  Use when implementing tool use, function calling, agent loops,

  or building AI assistants that interact with external systems.

  Trigger with phrases like "claude tool use", "anthropic function calling",

  "claude tools", "agent loop anthropic", "tool_use blocks".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- ai
- anthropic
compatibility: Designed for Claude Code
---
# Anthropic Core Workflow A — Tool Use (Function Calling)

## Overview

Implement Claude's tool use capability where the model can call functions you define. Claude returns `tool_use` content blocks with structured JSON inputs; your code executes the function and returns `tool_result` blocks. This is the foundation for building AI agents.

## Prerequisites

- Completed `anth-install-auth` setup
- Understanding of the Messages API request/response cycle
- Functions or APIs you want Claude to call

## Instructions

### Step 1: Define Tools

```python
import anthropic

client = anthropic.Anthropic()

tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a city. Use when the user asks about weather conditions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name, e.g. 'San Francisco, CA'"
                },
                "units": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature units"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "search_database",
        "description": "Search product database by query string. Returns matching products.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "integer", "default": 10}
            },
            "required": ["query"]
        }
    }
]
```

### Step 2: Send Request with Tools

```python
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}]
)

# Claude responds with stop_reason="tool_use"
# message.content contains both text and tool_use blocks:
# [
#   {"type": "text", "text": "I'll check the weather for you."},
#   {"type": "tool_use", "id": "toolu_01A...", "name": "get_weather",
#    "input": {"city": "Tokyo", "units": "celsius"}}
# ]
```

### Step 3: Execute Tool and Return Result

```python
def execute_tool(name: str, input_data: dict) -> str:
    """Route tool calls to actual implementations."""
    if name == "get_weather":
        # Call your weather API
        return '{"temp": 22, "condition": "partly cloudy", "humidity": 65}'
    elif name == "search_database":
        return '{"results": [{"name": "Widget A", "price": 29.99}]}'
    raise ValueError(f"Unknown tool: {name}")

# Extract tool_use blocks and execute
tool_results = []
for block in message.content:
    if block.type == "tool_use":
        result = execute_tool(block.name, block.input)
        tool_results.append({
            "type": "tool_result",
            "tool_use_id": block.id,  # Must match the tool_use block id
            "content": result
        })

# Continue conversation with tool results
follow_up = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "What's the weather in Tokyo?"},
        {"role": "assistant", "content": message.content},
        {"role": "user", "content": tool_results}
    ]
)

print(follow_up.content[0].text)
# "The current weather in Tokyo is 22°C and partly cloudy with 65% humidity."
```

### Step 4: Agentic Loop (Multiple Tool Calls)

```python
def run_agent(user_message: str, tools: list, max_turns: int = 10) -> str:
    """Run an agentic loop that handles multiple sequential tool calls."""
    messages = [{"role": "user", "content": user_message}]

    for _ in range(max_turns):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )

        # If Claude is done (no more tool calls), return final text
        if response.stop_reason == "end_turn":
            return next(
                (b.text for b in response.content if b.type == "text"), ""
            )

        # Process tool calls
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })
        messages.append({"role": "user", "content": tool_results})

    return "Max turns reached"
```

## Output

- Tool definitions with JSON Schema input validation
- Agent loop handling sequential tool calls
- Proper `tool_use` / `tool_result` message threading

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `invalid_request_error`: tool schema invalid | Malformed `input_schema` | Validate against JSON Schema spec |
| `tool_use_id` mismatch | Result ID doesn't match tool_use ID | Copy `block.id` exactly |
| Claude ignores tools | Description too vague | Add clear "Use when..." descriptions |
| Infinite loop | Claude keeps calling tools | Add `max_turns` guard + `tool_choice: {"type": "auto"}` |

## Tool Choice Options

```python
# Let Claude decide (default)
tool_choice={"type": "auto"}

# Force Claude to use a specific tool
tool_choice={"type": "tool", "name": "get_weather"}

# Force Claude to use any tool (must call at least one)
tool_choice={"type": "any"}
```

## Examples

For a support assistant, define `lookup_order` with an `order_id` string and
return a structured order status from the application database. Send the tool
result back using the original `block.id`; a successful run either returns an
`end_turn` response with the status in plain language or requests the next
tool needed to answer the user. Keep `max_turns` bounded so an unavailable
dependency fails predictably instead of looping.

## Resources

- [Tool Use Guide](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Tool Use API Reference](https://platform.claude.com/docs/en/api/messages)
- [Tool Use Examples](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)

## Next Steps

For streaming with tools, see `anth-core-workflow-b`.
