---
name: clade-core-workflow-b
description: 'Redirect to claude-embeddings-search for tool use (function calling)

  and agentic loop patterns with Claude.

  Use when looking for the secondary Anthropic workflow.

  Trigger with "anthropic tools", "claude function calling".

  '
allowed-tools: Read
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
compatibility: Designed for Claude Code
---
# Anthropic Core Workflow B → Tool Use

## Overview

This skill redirects to `clade-embeddings-search` which covers tool use (function calling), the agentic tool loop, and building Claude-powered agents.

## Prerequisites

- Completed `clade-model-inference`
- Understanding of JSON Schema for tool definitions

## Instructions

### Step 1: Use claude-embeddings-search instead

This skill has been replaced. The secondary Anthropic workflow is tool use / function calling, covered in full by `clade-embeddings-search`.

### Step 2: Key topics covered there

- Defining tools with JSON Schema input schemas
- Sending messages with tools attached
- Executing tool calls and returning results
- Building an agentic loop that runs until Claude stops calling tools
- Error handling for tool use edge cases

## Output

- Redirected to `clade-embeddings-search`
- Complete tool use patterns available there

## Error Handling

| Issue | Solution |
|-------|----------|
| Skill not found | Run `clade-embeddings-search` directly |
| Tool use errors | See tool validation patterns in that skill |

## Examples

```typescript
// Use claude-embeddings-search for the full tool use guide
const tools: Anthropic.Tool[] = [{
  name: 'get_weather',
  description: 'Get weather for a city',
  input_schema: {
    type: 'object',
    properties: { city: { type: 'string' } },
    required: ['city'],
  },
}];
const response = await client.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  tools,
  messages: [{ role: 'user', content: "What's the weather in Paris?" }],
});
```

## Resources

- [Tool Use Guide](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Tool Use API](https://platform.claude.com/docs/en/api/messages)

## Next Steps

Run `clade-embeddings-search` for the complete tool use guide.
