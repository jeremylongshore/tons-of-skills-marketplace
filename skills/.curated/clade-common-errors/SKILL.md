---
name: clade-common-errors
description: "Diagnose and fix Anthropic API errors \u2014 authentication, rate limits,\n\
  Use when working with common-errors patterns.\noverloaded, context length, and content\
  \ policy issues.\nTrigger with \"anthropic error\", \"claude 429\", \"claude overloaded\"\
  ,\n\"anthropic not working\", \"debug claude api\".\n"
allowed-tools: Read, Grep, Bash(curl:*)
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- errors
- debugging
compatibility: Designed for Claude Code
---
# Anthropic Common Errors

## Overview

Every Anthropic API error includes a `type` field and HTTP status code. Here are the real errors you'll hit and how to fix them.

## Error Reference

## Instructions

### Step 1: `authentication_error` (401)

```json
{"type":"error","error":{"type":"authentication_error","message":"invalid x-api-key"}}
```

**Cause:** API key is missing, malformed, or revoked.
**Fix:**

```bash
# Verify key exists and starts with sk-ant-
echo $ANTHROPIC_API_KEY | head -c 10
# Should print: sk-ant-api

# Test directly
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "claude-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
```

---

### Step 2: `rate_limit_error` (429)

```json
{"type":"error","error":{"type":"rate_limit_error","message":"Number of request tokens has exceeded your per-minute rate limit"}}
```

**Cause:** Exceeded requests per minute (RPM) or tokens per minute (TPM).
**Fix:**

```typescript
// The SDK has built-in retries with backoff
const client = new Anthropic({
  maxRetries: 3, // default is 2
});

// Or handle manually using the retry-after header
try {
  const msg = await client.messages.create({ ... });
} catch (err) {
  if (err instanceof Anthropic.RateLimitError) {
    const retryAfter = err.headers?.['retry-after'];
    await sleep(Number(retryAfter) * 1000 || 5000);
    // retry...
  }
}
```

**Rate limit tiers (as of 2025):**

| Tier | RPM | TPM (input) | TPM (output) |
|------|-----|-------------|--------------|
| Tier 1 (free) | 50 | 40,000 | 8,000 |
| Tier 2 ($40+) | 1,000 | 80,000 | 16,000 |
| Tier 3 ($200+) | 2,000 | 160,000 | 32,000 |
| Tier 4 ($400+) | 4,000 | 400,000 | 80,000 |

---

### Step 3: `overloaded_error` (529)

```json
{"type":"error","error":{"type":"overloaded_error","message":"Overloaded"}}
```

**Cause:** Anthropic API is temporarily at capacity. This is NOT a rate limit — it's server load.
**Fix:**

```typescript
// SDK retries 529s automatically. Increase retries if needed:
const client = new Anthropic({ maxRetries: 5 });

// For critical paths, implement fallback:
try {
  return await client.messages.create({ model: 'claude-sonnet-4-20250514', ... });
} catch (err) {
  if (err instanceof Anthropic.APIError && err.status === 529) {
    // Fall back to a different model or provider
    return await client.messages.create({ model: 'claude-haiku-4-5-20251001', ... });
  }
  throw err;
}
```

---

### Step 4: `invalid_request_error` (400)

```json
{"type":"error","error":{"type":"invalid_request_error","message":"messages: roles must alternate between \"user\" and \"assistant\", but found multiple \"user\" roles in a row"}}
```

**Common causes:**

- Messages don't alternate user/assistant
- `max_tokens` missing or exceeds model limit
- Image too large (>5MB) or wrong format
- Invalid `model` ID

**Fix:** Validate messages before sending:

```typescript
function validateMessages(messages: Anthropic.MessageParam[]) {
  for (let i = 1; i < messages.length; i++) {
    if (messages[i].role === messages[i - 1].role) {
      throw new Error(`Messages must alternate roles. Index ${i} has same role as ${i-1}`);
    }
  }
  if (messages[0]?.role !== 'user') {
    throw new Error('First message must be from user');
  }
}
```

---

### Step 5: `not_found_error` (404)

```json
{"type":"error","error":{"type":"not_found_error","message":"model: model_not_found"}}
```

**Cause:** Invalid model ID or model not available on your plan.
**Fix:** Use exact model IDs:

- `claude-opus-4-20250514`
- `claude-sonnet-4-20250514`
- `claude-haiku-4-5-20251001`

---

### Step 6: Content too long (context window)

```json
{"type":"error","error":{"type":"invalid_request_error","message":"prompt is too long: 204521 tokens > 200000 maximum"}}
```

**Fix:**

```typescript
// Count tokens before sending (use Anthropic's token counting)
const count = await client.messages.countTokens({
  model: 'claude-sonnet-4-20250514',
  messages,
});
console.log(`Input tokens: ${count.input_tokens}`);

if (count.input_tokens > 180000) {
  // Truncate conversation history, keeping system + last N messages
  messages = [messages[0], ...messages.slice(-10)];
}
```

## Quick Diagnostic

```bash
# Check API status
curl -s https://status.anthropic.com/api/v2/status.json | jq '.status.description'

# Verify API key works
curl -s https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "claude-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"ping"}]}' | jq '.content[0].text'

# Check current usage/limits
# (No API for this — check console.anthropic.com/settings/limits)
```

## Output

- Identified error type and HTTP status code
- Root cause determined from error message
- Applied fix (key rotation, backoff, input validation, model ID correction)
- Verified resolution with successful API call

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| API Error | Check error type and status code | See `clade-common-errors` |

## Examples

Each error section above includes the exact JSON error response, cause analysis, and fix code. See Quick Diagnostic section for curl commands to test connectivity.

## Resources

- [Error Types Reference](https://platform.claude.com/docs/en/api/errors)
- [Rate Limits](https://platform.claude.com/docs/en/api/rate-limits)
- [Anthropic Status](https://status.anthropic.com)

## Next Steps

For deeper debugging, see `clade-debug-bundle`.

## Prerequisites

- Anthropic SDK installed (`@claude-ai/sdk` or `anthropic`)
- API credentials configured
- Access to application logs or console output
