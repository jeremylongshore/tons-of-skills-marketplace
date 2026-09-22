---
name: clade-known-pitfalls
description: 'Common mistakes when building with the Anthropic API and how to avoid
  them.

  Use when working with known-pitfalls patterns.

  Trigger with "anthropic mistakes", "claude pitfalls", "anthropic gotchas",

  "common claude errors", "anthropic anti-patterns".

  '
allowed-tools: Read, Write, Edit
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- pitfalls
- best-practices
compatibility: Designed for Claude Code
---
# Anthropic Known Pitfalls

## Overview

Ten common mistakes when building with the Anthropic API and how to avoid them: forgetting `max_tokens` (required), system prompt in messages array (wrong), non-alternating messages, unchecked `stop_reason`, creating client per request, no 529 handling, hardcoded model IDs, expensive output tokens, no streaming, and unnecessary PII.

## 1. Forgetting `max_tokens`

Unlike OpenAI, `max_tokens` is **required**. Omitting it returns a 400 error.

```typescript
// BAD
await client.messages.create({ model: 'claude-sonnet-4-20250514', messages });

// GOOD
await client.messages.create({ model: 'claude-sonnet-4-20250514', max_tokens: 1024, messages });
```

## 2. System Prompt in Messages Array

Claude uses a top-level `system` parameter, not a system message in the array.

```typescript
// BAD — this sends "system" as a user message role, which will error
messages: [{ role: 'system', content: '...' }, { role: 'user', content: '...' }]

// GOOD
system: 'You are helpful.',
messages: [{ role: 'user', content: '...' }]
```

## 3. Non-Alternating Messages

Messages must strictly alternate between user and assistant.

```typescript
// BAD — two user messages in a row
messages: [
  { role: 'user', content: 'Hello' },
  { role: 'user', content: 'How are you?' }, // ERROR
]

// GOOD — combine into one or add assistant between
messages: [
  { role: 'user', content: 'Hello. How are you?' },
]
```

## 4. Not Checking `stop_reason`

If `stop_reason === 'max_tokens'`, the response was truncated.

```typescript
if (message.stop_reason === 'max_tokens') {
  // Response is incomplete — increase max_tokens or handle truncation
}
```

## 5. Creating Client Per Request

Each `new Anthropic()` creates a new connection pool. In serverless, this adds latency.

```typescript
// BAD — new client every request
app.post('/chat', async (req, res) => {
  const client = new Anthropic(); // Cold connection every time
});

// GOOD — reuse across requests
const client = new Anthropic();
app.post('/chat', async (req, res) => {
  await client.messages.create({ ... });
});
```

## 6. No Error Handling for 529

529 (overloaded) is common during peak hours. The SDK retries automatically, but you should handle it for critical paths.

## 7. Hardcoding Model IDs

Model IDs change with new versions. Use environment variables.

```typescript
const MODEL = process.env.CLAUDE_MODEL || 'claude-sonnet-4-20250514';
```

## 8. Ignoring Token Costs

Output tokens cost 5x more than input tokens. A 4096 max_tokens response on Opus costs ~$0.30. Use the smallest max_tokens that works.

## 9. No Streaming for User-Facing Apps

Without streaming, users stare at a blank screen for 5-30 seconds. Always stream for interactive use.

## 10. Sending PII Unnecessarily

Don't include user PII in prompts unless the task requires it. Redact before sending.

## Quick Reference

| Pitfall | Fix |
|---------|-----|
| Missing `max_tokens` | Always include it |
| System in messages | Use top-level `system` param |
| Non-alternating messages | Combine or interleave |
| Unchecked `stop_reason` | Check for `max_tokens` truncation |
| Client per request | Module-level singleton |
| No 529 handling | SDK retries + fallback model |
| Hardcoded model IDs | Environment variable |
| Expensive output | Minimize `max_tokens` |
| No streaming | Always stream for UI |
| Unnecessary PII | Redact before sending |

## Output

- All ten pitfalls checked against your codebase
- `max_tokens` present on every `messages.create` call
- System prompt using top-level `system` parameter
- Messages strictly alternating user/assistant
- `stop_reason` checked for truncation
- Client instance reused across requests

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| API Error | Check error type and status code | See `clade-common-errors` |

## Examples

See ten numbered pitfall sections above, each with BAD/GOOD code comparisons. Quick Reference table at the end summarizes all fixes.

## Resources

- [API Reference](https://platform.claude.com/docs/en/api/messages)
- [Best Practices](https://platform.claude.com/docs/en/build-with-claude/overview)

## Prerequisites

- Familiarity with the Anthropic Messages API
- Active Claude integration to audit
- Access to codebase for pattern review

## Instructions

### Step 1: Review the patterns below

Each section contains production-ready code examples. Copy and adapt them to your use case.

### Step 2: Apply to your codebase

Integrate the patterns that match your requirements. Test each change individually.

### Step 3: Verify

Run your test suite to confirm the integration works correctly.
