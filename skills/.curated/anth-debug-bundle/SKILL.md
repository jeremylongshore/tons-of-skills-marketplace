---
name: anth-debug-bundle
description: 'Collect Anthropic Claude API debug evidence for support and troubleshooting.

  Use when encountering persistent API issues, preparing support tickets,

  or collecting diagnostic information including request IDs and rate limit headers.

  Trigger with phrases like "anthropic debug", "claude debug bundle",

  "collect anthropic logs", "anthropic diagnostic", "claude support ticket".

  '
allowed-tools: Read, Bash(grep:*), Bash(curl:*), Bash(tar:*), Grep
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- ai
- anthropic
compatibility: Designed for Claude Code
---
# Anthropic Debug Bundle

## Overview

Collect diagnostic information for Claude API issues. Every API response includes a `request-id` header — this is the single most important piece of data for Anthropic support.

## Prerequisites

- Anthropic SDK installed
- Access to application logs
- `ANTHROPIC_API_KEY` set in environment

## Instructions

### Step 1: Capture Request ID

```python
import anthropic

client = anthropic.Anthropic()

try:
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=64,
        messages=[{"role": "user", "content": "test"}]
    )
    print(f"Request ID: {message._request_id}")  # req_01A1B2C3...
except anthropic.APIStatusError as e:
    print(f"Request ID: {e.response.headers.get('request-id')}")
    print(f"Status: {e.status_code}")
    print(f"Error: {e.message}")
```

```typescript
// TypeScript — access raw response headers
const response = await client.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 64,
  messages: [{ role: 'user', content: 'test' }],
}).asResponse();

console.log('Request ID:', response.headers.get('request-id'));
console.log('Rate limit remaining:', response.headers.get('anthropic-ratelimit-requests-remaining'));
```

### Step 2: Debug Bundle Script

```bash
#!/bin/bash
# anthropic-debug-bundle.sh
BUNDLE_DIR="anthropic-debug-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BUNDLE_DIR"

echo "=== Anthropic Debug Bundle ===" > "$BUNDLE_DIR/summary.txt"
echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$BUNDLE_DIR/summary.txt"

# SDK versions
echo -e "\n--- SDK Versions ---" >> "$BUNDLE_DIR/summary.txt"
pip show anthropic 2>/dev/null | grep -E "^(Name|Version)" >> "$BUNDLE_DIR/summary.txt"
npm list @anthropic-ai/sdk 2>/dev/null >> "$BUNDLE_DIR/summary.txt"
python3 --version >> "$BUNDLE_DIR/summary.txt" 2>&1
node --version >> "$BUNDLE_DIR/summary.txt" 2>&1

# API key status (NEVER log the key itself)
echo -e "\n--- Auth Status ---" >> "$BUNDLE_DIR/summary.txt"
echo "ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:+SET (${#ANTHROPIC_API_KEY} chars)}" >> "$BUNDLE_DIR/summary.txt"

# Connectivity test with headers
echo -e "\n--- API Connectivity ---" >> "$BUNDLE_DIR/summary.txt"
curl -s -w "\nHTTP %{http_code} | Time: %{time_total}s" \
  -o "$BUNDLE_DIR/api-response.json" \
  -D "$BUNDLE_DIR/response-headers.txt" \
  https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":8,"messages":[{"role":"user","content":"1"}]}' \
  >> "$BUNDLE_DIR/summary.txt"

# Rate limit headers
echo -e "\n--- Rate Limit Headers ---" >> "$BUNDLE_DIR/summary.txt"
grep -i "ratelimit\|request-id\|retry-after" "$BUNDLE_DIR/response-headers.txt" >> "$BUNDLE_DIR/summary.txt"

# API status page
echo -e "\n--- API Status ---" >> "$BUNDLE_DIR/summary.txt"
curl -s https://status.anthropic.com/api/v2/status.json | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d['status']['description'])" >> "$BUNDLE_DIR/summary.txt" 2>&1

# Package and clean up
tar -czf "$BUNDLE_DIR.tar.gz" "$BUNDLE_DIR"
rm -rf "$BUNDLE_DIR"
echo "Bundle: $BUNDLE_DIR.tar.gz"
```

### Step 3: Redaction Rules

**ALWAYS REDACT:** API keys, user content/PII, authorization headers

**SAFE TO INCLUDE:** Request IDs, error messages, rate limit headers, SDK versions, status codes, timestamps

## Output

The result is a timestamped compressed bundle containing a redacted summary,
SDK and runtime versions, connection status, response headers, and request IDs
that support can correlate. It must not contain an API key, authorization
header, or customer prompt/response content; inspect the archive before it is
attached to a ticket.

## Error Handling

If the connectivity request returns an HTTP error, retain its status, request
ID, and rate-limit headers in the bundle and record the time of the attempt. If
the status endpoint or package lookup is unavailable, note that collection step
as unavailable rather than inventing a result. If redaction cannot be verified,
do not share the archive; recreate it after removing the unsafe source data.

## Examples

When a production request repeatedly receives a 429, capture the request ID
from the SDK exception, run the bundle script in a controlled environment, and
attach only the reviewed archive plus the affected time window to support. When
a response appears malformed, include the SDK version and a redacted error
message, but replace the original user prompt with a short synthetic example
that reproduces the behavior.

## Key Headers for Debugging

| Header | Example | Use |
|--------|---------|-----|
| `request-id` | `req_01A1B2C3...` | Support ticket reference |
| `anthropic-ratelimit-requests-limit` | `1000` | Your RPM cap |
| `anthropic-ratelimit-requests-remaining` | `995` | Requests left |
| `anthropic-ratelimit-tokens-limit` | `80000` | Your TPM cap |
| `anthropic-ratelimit-tokens-remaining` | `79000` | Tokens left |
| `retry-after` | `30` | Seconds to wait (on 429) |

## Resources

- [API Status](https://status.anthropic.com)
- [Error Types](https://platform.claude.com/docs/en/api/errors)
- [Rate Limits](https://platform.claude.com/docs/en/api/rate-limits)

## Next Steps

For rate limit issues, see `anth-rate-limits`.
