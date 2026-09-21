---
name: clade-core-workflow-a
description: 'Redirect to claude-model-inference for Messages API streaming,

  vision, and structured output patterns.

  Use when looking for the primary Anthropic workflow.

  Trigger with "anthropic workflow", "claude main workflow".

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
# Anthropic Core Workflow A → Model Inference

## Overview

This skill redirects to `clade-model-inference` which covers streaming, vision, structured output, and all Messages API patterns.

## Prerequisites

- Completed `clade-install-auth` setup
- `ANTHROPIC_API_KEY` configured

## Instructions

### Step 1: Use claude-model-inference instead

This skill has been replaced. The primary Anthropic workflow is the Messages API, covered in full by `clade-model-inference`.

### Step 2: Key topics covered there

- Streaming responses with `client.messages.stream()`
- Vision — sending images to Claude
- Structured JSON output via system prompts
- Multi-turn conversations
- All Messages API parameters

## Output

- Redirected to `clade-model-inference`
- All Messages API patterns available there

## Error Handling

| Issue | Solution |
|-------|----------|
| Skill not found | Run `clade-model-inference` directly |

## Examples

```typescript
// Use claude-model-inference for the full Messages API guide
import Anthropic from '@claude-ai/sdk';
const client = new Anthropic();
const stream = client.messages.stream({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  messages: [{ role: 'user', content: 'Hello!' }],
});
```

## Resources

- [Messages API](https://platform.claude.com/docs/en/api/messages)
- [Streaming](https://platform.claude.com/docs/en/build-with-claude/streaming)

## Next Steps

Run `clade-model-inference` for the complete guide.
