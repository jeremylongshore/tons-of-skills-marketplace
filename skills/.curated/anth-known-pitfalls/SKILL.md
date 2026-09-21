---
name: anth-known-pitfalls
description: 'Identify and avoid common Claude API anti-patterns and integration mistakes.

  Use when reviewing code, onboarding developers, or debugging subtle issues

  with Anthropic integrations.

  Trigger with phrases like "anthropic pitfalls", "claude anti-patterns",

  "claude mistakes", "anthropic common issues", "claude gotchas".

  '
allowed-tools: Read, Write, Edit, Grep
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- ai
- anthropic
compatibility: Designed for Claude Code
---
# Anthropic Known Pitfalls

## Overview

This reference is a review aid for common Anthropic API integration mistakes. Apply the checks to the actual SDK/API version in use and confirm changing behavior against Anthropic’s current documentation before making a compatibility claim.

## Pitfall 1: Wrong Import / Class Name

```python
# WRONG — common mistake from OpenAI muscle memory
from anthropic import AnthropicClient  # Does not exist

# CORRECT
import anthropic
client = anthropic.Anthropic()
```

```typescript
// WRONG
import { Anthropic } from '@anthropic-ai/sdk';

// CORRECT
import Anthropic from '@anthropic-ai/sdk';  // Default export
```

## Pitfall 2: Forgetting max_tokens (Required)

```python
# WRONG — max_tokens is REQUIRED, unlike OpenAI
msg = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "Hello"}]
)  # Error: max_tokens is required

# CORRECT
msg = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,  # Always specify
    messages=[{"role": "user", "content": "Hello"}]
)
```

## Pitfall 3: System Prompt in Messages Array

```python
# WRONG — putting system message in messages array (OpenAI pattern)
messages = [
    {"role": "system", "content": "You are helpful."},  # Will cause error
    {"role": "user", "content": "Hello"}
]

# CORRECT — use the system parameter
msg = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system="You are helpful.",  # Separate parameter
    messages=[{"role": "user", "content": "Hello"}]
)
```

## Pitfall 4: Accessing Response Wrong

```python
# WRONG — OpenAI response pattern
text = response.choices[0].message.content  # AttributeError

# CORRECT — Anthropic response pattern
text = response.content[0].text  # content is array of blocks

# SAFER — handle multiple content blocks
text_blocks = [b.text for b in response.content if b.type == "text"]
text = "\n".join(text_blocks)
```

## Pitfall 5: Ignoring Stop Reason

```python
# WRONG — assuming response is always complete
text = msg.content[0].text  # Might be truncated!

# CORRECT — check stop_reason
if msg.stop_reason == "max_tokens":
    print("WARNING: Response was truncated. Increase max_tokens.")
elif msg.stop_reason == "tool_use":
    print("Claude wants to call a tool — process tool_use blocks")
elif msg.stop_reason == "end_turn":
    print("Complete response")
```

## Pitfall 6: Not Handling tool_use_id Properly

```python
# WRONG — fabricating tool_use_id
tool_results = [{"type": "tool_result", "tool_use_id": "some-id", "content": "..."}]

# CORRECT — use the exact ID from Claude's response
for block in response.content:
    if block.type == "tool_use":
        result = execute_tool(block.name, block.input)
        tool_results.append({
            "type": "tool_result",
            "tool_use_id": block.id,  # Must match exactly
            "content": result
        })
```

## Pitfall 7: Hardcoding Model IDs Without Versioning

```python
# RISKY — model aliases may change behavior
model = "claude-3-5-sonnet"  # Alias, might point to different version

# BETTER — use dated version for reproducibility
model = "claude-sonnet-4-20250514"  # Pinned version
```

## Pitfall 8: Not Using SDK Auto-Retry

```python
# UNNECESSARY — writing custom retry logic for 429/5xx
for attempt in range(3):
    try:
        msg = client.messages.create(...)
        break
    except Exception:
        time.sleep(2 ** attempt)

# BETTER — SDK handles this automatically
client = anthropic.Anthropic(max_retries=5)  # Built-in exponential backoff
msg = client.messages.create(...)  # Auto-retries 429 and 5xx
```

## Pitfall 9: Inflated max_tokens

```python
# WASTEFUL — setting max_tokens higher than needed
# Doesn't cost more tokens, but increases latency
msg = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=200000,  # Way more than needed for a classification
    messages=[{"role": "user", "content": "Classify: positive or negative?"}]
)

# BETTER — right-size for the task
msg = client.messages.create(
    model="claude-haiku-4-20250514",  # Use Haiku for classification
    max_tokens=16,  # Only need one word
    messages=[{"role": "user", "content": "Classify: positive or negative?"}]
)
```

## Pitfall 10: No Cost Tracking

```python
# Every response includes usage data — track it
msg = client.messages.create(...)
cost = (msg.usage.input_tokens * 3.0 + msg.usage.output_tokens * 15.0) / 1_000_000
# Log cost per request to catch runaway spend early
```

## Quick Reference: Anthropic vs OpenAI Differences

| Feature | OpenAI | Anthropic |
|---------|--------|-----------|
| `max_tokens` | Optional | **Required** |
| System prompt | In messages array | `system` parameter |
| Response text | `.choices[0].message.content` | `.content[0].text` |
| Default import | Named export | Default export |
| Auto-retry | No | Yes (configurable) |
| Streaming | Yields chunks | SSE events |

## Prerequisites

- Identify the SDK/runtime versions, pinned model IDs, request paths, tool definitions, data classification, and owner of the integration.
- Use a sandbox workspace, synthetic prompts, least-privileged credentials, and a redaction policy for review and reproduction; do not paste production content or keys into diagnostics.
- Define acceptance checks for authentication, request shape, stop reasons, tool IDs, retries, token budgets, cost, and logging hygiene.

## Instructions

1. Review imports, request construction, response parsing, model/version pins, retry behavior, and token limits against the installed SDK and official API reference.
2. Exercise each suspected pitfall with synthetic fixtures, including malformed requests, truncated output, tool calls, 429/5xx, timeout, and duplicate retry cases. Assert no sensitive content appears in logs or receipts.
3. Check that authentication comes from the secret manager, permissions and model/workspace scope are enforced, and retries are bounded and safe for the operation.
4. Canary corrective changes in an isolated workspace and compare response-shape, latency, cost, and error aggregates with the baseline. Require approval before production rollout.
5. For a failed gate, quarantine affected output, restore the prior revision, revoke temporary access if needed, and record a redacted finding with the documented remediation.

## Output

Produce a pitfall-review receipt listing SDK/API versions, checks run, synthetic fixture classes, findings and severity, response-shape/error aggregates, logging/redaction result, canary and approval state, and rollback reference. Exclude prompt/response text, personal data, member information, and credentials.

## Error Handling

| Finding | Response |
|---|---|
| Request-shape or import mismatch | Pin the compatible SDK, update the code under test, and rerun contract tests. |
| Missing/incorrect stop or tool handling | Reject or quarantine the result; use the exact response metadata and tool-use ID. |
| Unbounded retry or inflated token budget | Apply bounded retry/idempotency controls and a role/budget-specific token cap. |
| Content or secret appears in telemetry | Stop the canary, rotate exposed credentials if applicable, purge according to retention policy, and fix the redaction boundary. |

## Examples

Run a sandbox review using `fixture-tool-call-001` and `fixture-truncated-002`, assert `tool_use_id_match=1; stop_reason_checked=1; content_logged=0`, and emit `pitfalls=0; canary=internal; rollback=integration-v1`. Never reproduce a failure with a live customer prompt.

## Resources

- [Messages API Reference](https://platform.claude.com/docs/en/api/messages)
- [Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- [TypeScript SDK](https://github.com/anthropics/anthropic-sdk-typescript)
