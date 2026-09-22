---
name: clade-migration-deep-dive
description: "Migrate from OpenAI/GPT to Anthropic/Claude \u2014 API differences,\n\
  Use when working with migration-deep-dive patterns.\nprompt adaptation, SDK swap,\
  \ and feature mapping.\nTrigger with \"migrate to claude\", \"openai to anthropic\"\
  ,\n\"switch from gpt to claude\", \"replace openai with anthropic\".\n"
allowed-tools: Read, Write, Edit, Grep
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- migration
- openai
compatibility: Designed for Claude Code
---
# Migrate from OpenAI to Anthropic

## Overview

Migrate from OpenAI/GPT to Anthropic/Claude. Covers the complete API mapping (endpoints, models, response shapes), SDK swap with before/after code, five key differences (max_tokens required, system as top-level param, alternating messages, response path, streaming events), and tool use migration.

## API Mapping

| OpenAI | Anthropic | Notes |
|--------|-----------|-------|
| `openai.chat.completions.create()` | `anthropic.messages.create()` | Different request/response shape |
| `model: 'gpt-4o'` | `model: 'claude-sonnet-4-20250514'` | Different model IDs |
| `response.choices[0].message.content` | `response.content[0].text` | Different response path |
| `system` in messages array | `system` as separate parameter | Claude uses top-level `system` |
| `response_format: { type: 'json_object' }` | System prompt: "Respond in JSON only" | No native JSON mode |
| `tools` / `function_calling` | `tools` (similar but different schema) | Input schema differences |
| `openai.embeddings.create()` | N/A — use Voyage or Cohere | No embeddings API |

## SDK Swap

## Instructions

### Step 1: Before (OpenAI)

```typescript
import OpenAI from 'openai';
const openai = new OpenAI();

const response = await openai.chat.completions.create({
  model: 'gpt-4o',
  messages: [
    { role: 'system', content: 'You are helpful.' },
    { role: 'user', content: 'Hello' },
  ],
});
console.log(response.choices[0].message.content);
```

### Step 2: After (Anthropic)

```typescript
import Anthropic from '@claude-ai/sdk';
const anthropic = new Anthropic();

const response = await anthropic.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024, // Required (not optional like OpenAI)
  system: 'You are helpful.', // Separate from messages
  messages: [
    { role: 'user', content: 'Hello' },
  ],
});
console.log(response.content[0].text);
```

## Key Differences

1. **`max_tokens` is required** — OpenAI defaults it, Anthropic requires it
2. **`system` is a top-level param** — not a message in the array
3. **First message must be `user`** — can't start with assistant
4. **Messages must alternate** — no two user or two assistant messages in a row
5. **Response shape** — `content[0].text` not `choices[0].message.content`
6. **Streaming events** — different event types and structure

## Tool Use Migration

```typescript
// OpenAI tool definition
{ type: 'function', function: { name: 'get_weather', parameters: { ... } } }

// Anthropic tool definition
{ name: 'get_weather', input_schema: { ... } }  // Flatter structure
```

## Grep & Replace

```bash
# Find all OpenAI imports
grep -rn "from 'openai'" --include="*.ts" .
grep -rn "import OpenAI" --include="*.ts" .

# Find response access patterns to update
grep -rn "choices\[0\]" --include="*.ts" .
grep -rn "message.content" --include="*.ts" .  # May need updating
```

## Output

- All `openai` imports replaced with `@claude-ai/sdk`
- Response access patterns updated (`choices[0].message.content` → `content[0].text`)
- System prompts moved from messages array to top-level `system` parameter
- `max_tokens` added to all API calls (required, not optional)
- Tool definitions restructured to Anthropic format

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| API Error | Check error type and status code | See `clade-common-errors` |

## Examples

See API Mapping table, Before/After SDK code, Key Differences list, Tool Use Migration, and Grep & Replace commands above.

## Resources

- [Anthropic Messages API](https://platform.claude.com/docs/en/api/messages)
- [Migration Guide](https://platform.claude.com/docs/en/models/overview)

## Next Steps

See `clade-sdk-patterns` for production Anthropic SDK patterns.

## Prerequisites

- Existing OpenAI integration to migrate
- Access to codebase with search capability
- Test suite for comparing outputs between providers
