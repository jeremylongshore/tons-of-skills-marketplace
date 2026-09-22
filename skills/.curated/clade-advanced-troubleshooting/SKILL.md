---
name: clade-advanced-troubleshooting
description: "Debug complex Claude issues \u2014 inconsistent outputs, tool use failures,\n\
  Use when working with advanced-troubleshooting patterns.\nstreaming problems, and\
  \ edge cases.\nTrigger with \"claude inconsistent\", \"anthropic advanced debug\"\
  ,\n\"claude tool use broken\", \"anthropic streaming issues\".\n"
allowed-tools: Read, Write, Edit, Grep, Bash(curl:*)
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- debugging
- advanced
compatibility: Designed for Claude Code
---
# Anthropic Advanced Troubleshooting

## Overview

Debug complex Claude integration issues that go beyond basic error handling — inconsistent outputs, tool use failures where Claude calls nonexistent tools, streaming connection drops, max_tokens truncation, and image/vision format problems.

## Inconsistent Outputs

**Symptom:** Same prompt gives different answers each time.
**Cause:** `temperature` defaults to 1.0 (maximum randomness).

```typescript
// Fix: Set temperature to 0 for deterministic outputs
const message = await client.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  temperature: 0, // Deterministic
  messages,
});
```

## Tool Use Failures

**Symptom:** Claude calls a tool that doesn't exist or sends wrong parameters.

```typescript
// Always validate tool calls before executing
const toolUse = response.content.find(b => b.type === 'tool_use');
if (toolUse) {
  const validTools = tools.map(t => t.name);
  if (!validTools.includes(toolUse.name)) {
    console.error(`Claude requested unknown tool: ${toolUse.name}`);
    // Send error back as tool_result
    messages.push({ role: 'assistant', content: response.content });
    messages.push({ role: 'user', content: [{
      type: 'tool_result',
      tool_use_id: toolUse.id,
      is_error: true,
      content: `Tool "${toolUse.name}" does not exist. Available: ${validTools.join(', ')}`,
    }]});
  }
}
```

## Streaming Connection Drops

**Symptom:** Stream stops mid-response without `message_stop` event.

```typescript
// Detect incomplete streams
const stream = client.messages.stream({ ... });
let gotStop = false;

for await (const event of stream) {
  if (event.type === 'message_stop') gotStop = true;
  // ... process events
}

if (!gotStop) {
  console.error('Stream ended without message_stop — connection dropped');
  // Retry the request
}
```

## `max_tokens` Truncation

**Symptom:** Response cuts off mid-sentence.

```typescript
const message = await client.messages.create({ ... });

if (message.stop_reason === 'max_tokens') {
  console.warn('Response truncated — increase max_tokens or ask for shorter output');
  // Option 1: Increase max_tokens
  // Option 2: Add "Be concise" to system prompt
  // Option 3: Continue the response with another call
}
```

## Image/Vision Issues

**Symptom:** Claude says it can't see the image.

- Max image size: 5MB
- Supported: PNG, JPEG, GIF, WebP
- Max 20 images per request
- Base64 encoding must be correct (no data URI prefix in the `data` field)

```typescript
// Correct image format
{
  type: 'image',
  source: {
    type: 'base64',
    media_type: 'image/png', // Must match actual format
    data: buffer.toString('base64'), // Raw base64, no "data:image/png;base64," prefix
  },
}
```

## Output

- Inconsistent outputs fixed via temperature control
- Tool use validated against defined tool names before execution
- Streaming connection drops detected and retried
- Truncated responses identified via `stop_reason` check
- Image format issues resolved (correct media_type, raw base64, size limits)

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| API Error | Check error type and status code | See `clade-common-errors` |

## Examples

See Inconsistent Outputs (temperature fix), Tool Use Failures (validation), Streaming Connection Drops (detection), max_tokens Truncation (stop_reason check), and Image/Vision Issues (correct format) above.

## Resources

- [Error Types](https://platform.claude.com/docs/en/api/errors)
- [Tool Use Guide](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Vision Docs](https://platform.claude.com/docs/en/build-with-claude/vision)

## Next Steps

See `clade-debug-bundle` for collecting support evidence.

## Prerequisites

- Completed `clade-common-errors` for basic error handling
- Familiarity with Claude API response structure
- Access to application logs with full request/response data

## Instructions

### Step 1: Review the patterns below

Each section contains production-ready code examples. Copy and adapt them to your use case.

### Step 2: Apply to your codebase

Integrate the patterns that match your requirements. Test each change individually.

### Step 3: Verify

Run your test suite to confirm the integration works correctly.
