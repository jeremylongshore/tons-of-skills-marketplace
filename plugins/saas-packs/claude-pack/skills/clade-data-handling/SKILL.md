---
name: clade-data-handling
description: "Handle sensitive data with Claude \u2014 PII redaction, conversation\
  \ management,\nUse when working with data-handling patterns.\ncontext window optimization,\
  \ and data retention policies.\nTrigger with \"anthropic data privacy\", \"claude\
  \ pii\", \"anthropic context window\",\n\"manage claude conversations\", \"anthropic\
  \ data retention\".\n"
allowed-tools: Read, Write, Edit
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- data
- privacy
- context
compatibility: Designed for Claude Code
---
# Anthropic Data Handling

## Overview

Handle data responsibly when building with Claude — manage the 200K token context window efficiently, implement conversation trimming strategies, redact PII before sending to the API, and configure data retention settings.

## Context Window Management

Claude models have a 200K token context window. Managing it efficiently is critical.

```typescript
// Count tokens before sending
const count = await client.messages.countTokens({
  model: 'claude-sonnet-4-20250514',
  messages,
  system: systemPrompt,
});

// Budget: 200K total - max_tokens (output) = available input
const MAX_CONTEXT = 200_000;
const MAX_OUTPUT = 4096;
const inputBudget = MAX_CONTEXT - MAX_OUTPUT;

if (count.input_tokens > inputBudget) {
  // Trim oldest messages, keep system prompt + recent context
  messages = trimToFit(messages, inputBudget);
}
```

## Instructions

### Step 1: Conversation Trimming

```typescript
function trimConversation(messages: MessageParam[], maxTokens: number): MessageParam[] {
  // Always keep the first message (often contains key context)
  // Keep the most recent messages
  // Drop middle turns first
  if (messages.length <= 4) return messages;

  const first = messages[0];
  const recent = messages.slice(-6); // Last 3 turns
  return [first, ...recent];
}
```

## PII Handling

```typescript
// Strip PII before sending to Claude (if not needed for the task)
function redactPII(text: string): string {
  return text
    .replace(/\b[\w._%+-]+@[\w.-]+\.\w{2,}\b/g, '[EMAIL]')
    .replace(/\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g, '[PHONE]')
    .replace(/\b\d{3}-\d{2}-\d{4}\b/g, '[SSN]')
    .replace(/\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g, '[CARD]');
}
```

## Data Retention

- **Default**: Anthropic does not use API data for training
- **Zero retention**: Available on Enterprise plans
- **Your responsibility**: Don't store Claude responses containing user PII longer than needed

## Output

- Token counting implemented before sending requests (prevents context overflow errors)
- Conversation trimming preserving first message and recent turns
- PII redaction applied for emails, phone numbers, SSNs, and card numbers
- Data retention policy documented and configured

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| API Error | Check error type and status code | See `clade-common-errors` |

## Examples

See Context Window Management (token counting + budget), Conversation Trimming function, and PII Handling regex patterns above.

## Resources

- Anthropic Privacy Policy
- [Token Counting](https://platform.claude.com/docs/en/api/messages/count_tokens)
- [Context Window](https://platform.claude.com/docs/en/models/overview)

## Next Steps

See `clade-enterprise-rbac` for organization and access management.

## Prerequisites

- Completed `clade-install-auth`
- Application handling user conversations or document processing
- Understanding of token counting and context windows
