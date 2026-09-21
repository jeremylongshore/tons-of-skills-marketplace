---
name: clade-debug-bundle
description: "Collect debug evidence for Anthropic API issues \u2014 request IDs,\
  \ headers,\nUse when working with debug-bundle patterns.\nerror payloads, and reproduction\
  \ steps for support tickets.\nTrigger with \"anthropic debug\", \"claude support\
  \ ticket\", \"anthropic request id\",\n\"debug claude api call\".\n"
allowed-tools: Read, Grep, Bash(curl:*)
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- debugging
compatibility: Designed for Claude Code
---
# Anthropic Debug Bundle

## Overview

When you need to file a support ticket or debug a persistent issue, collect these items.

## Prerequisites

- Anthropic SDK installed
- An API error or issue to debug
- Access to application logs

## Instructions

### Step 1: Get the Request ID

Every Anthropic API response includes a `request-id` header. This is the single most important thing for support tickets.

```typescript
try {
  const message = await client.messages.create({ ... });
  // Access response headers via the raw response
} catch (err) {
  if (err instanceof Anthropic.APIError) {
    console.error('Request ID:', err.headers?.['request-id']);
    console.error('Status:', err.status);
    console.error('Error type:', err.error?.type);
    console.error('Message:', err.message);
  }
}
```

### Step 2: Log Full Error Details

```typescript
function logAnthropicError(err: unknown) {
  if (err instanceof Anthropic.APIError) {
    const bundle = {
      timestamp: new Date().toISOString(),
      request_id: err.headers?.['request-id'],
      status: err.status,
      error_type: err.error?.type,
      error_message: err.message,
      rate_limit_remaining: err.headers?.['claude-ratelimit-requests-remaining'],
      rate_limit_reset: err.headers?.['claude-ratelimit-requests-reset'],
    };
    console.error('Anthropic Debug Bundle:', JSON.stringify(bundle, null, 2));
    return bundle;
  }
  console.error('Non-API error:', err);
}
```

### Step 3: Test with curl

```bash
# Minimal reproduction — include this in support tickets
curl -v https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "claude-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "test"}]
  }' 2>&1 | grep -E "request-id|HTTP|error"
```

### Step 4: Check Status

```bash
# API status
curl -s https://status.anthropic.com/api/v2/status.json | python3 -m json.tool

# Recent incidents
curl -s https://status.anthropic.com/api/v2/incidents.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for inc in data['incidents'][:3]:
    print(f\"{inc['created_at'][:10]}: {inc['name']} ({inc['status']})\")
"
```

## What to Include in Support Tickets

1. **Request ID** (from `request-id` header)
2. **Timestamp** (UTC)
3. **Model** used
4. **Error type and message** (full JSON)
5. **curl reproduction** (sanitize your API key)
6. **SDK version** (`npm list @claude-ai/sdk` or `pip show anthropic`)

## Python Debug

```python
try:
    message = client.messages.create(...)
except anthropic.APIStatusError as e:
    print(f"Request ID: {e.response.headers.get('request-id')}")
    print(f"Status: {e.status_code}")
    print(f"Error: {e.message}")
```

## Output

- Request ID extracted from error response headers
- Full error bundle with timestamp, status, error type, and rate limit state
- curl command for minimal reproduction (ready to paste into support ticket)
- Anthropic API status and recent incidents checked

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| API Error | Check error type and status code | See `clade-common-errors` |

## Examples

See Step 1 (request ID extraction), Step 2 (full error logging), Step 3 (curl reproduction), and Step 4 (status check) above.

## Resources

- [Anthropic Status](https://status.anthropic.com)
- [Error Types](https://platform.claude.com/docs/en/api/errors)
- [Support](https://support.anthropic.com)

## Next Steps

See `clade-common-errors` for specific error solutions.
