---
name: anth-common-errors
description: 'Diagnose and fix Anthropic Claude API errors by HTTP status code.

  Use when encountering API errors, debugging failed requests,

  or troubleshooting authentication, rate limiting, or input validation issues.

  Trigger with phrases like "anthropic error", "claude api error",

  "fix anthropic 429", "claude not working", "debug claude api".

  '
allowed-tools: Read, Grep, Bash(curl:*)
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- ai
- anthropic
compatibility: Designed for Claude Code
---
# Anthropic Common Errors

## Overview

Quick reference for all Claude API error types with exact HTTP codes, error bodies, and fixes. The API returns errors as JSON: `{"type": "error", "error": {"type": "...", "message": "..."}}`.

## Error Reference

### 400 — `invalid_request_error`

```json
{"type": "error", "error": {"type": "invalid_request_error", "message": "messages: roles must alternate between \"user\" and \"assistant\""}}
```

**Common causes and fixes:**

| Message Pattern | Cause | Fix |
|----------------|-------|-----|
| `messages: roles must alternate` | Consecutive same-role messages | Merge adjacent user/assistant messages |
| `max_tokens: must be >= 1` | Missing or zero `max_tokens` | Always set `max_tokens` (required param) |
| `model: invalid model id` | Typo in model name | Use exact ID: `claude-sonnet-4-20250514` |
| `messages.0.content: empty` | Empty message content | Ensure content is non-empty string or array |
| `tool_result: tool_use_id not found` | Mismatched tool ID | Copy `id` from the `tool_use` block exactly |

### 401 — `authentication_error`

```bash
# Verify your key is set and valid
echo $ANTHROPIC_API_KEY | head -c 15  # Should show: sk-ant-api03-...

# Test directly with curl
curl -s https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":16,"messages":[{"role":"user","content":"hi"}]}'
```

### 403 — `permission_error`

API key lacks required permissions. Generate a new key at [console.anthropic.com](https://console.anthropic.com).

### 404 — `not_found_error`

Invalid endpoint or model. Check you're using `https://api.anthropic.com/v1/messages` and a valid model ID.

### 429 — `rate_limit_error`

```json
{"type": "error", "error": {"type": "rate_limit_error", "message": "Number of request tokens has exceeded your per-minute rate limit"}}
```

**Check headers for details:**

- `retry-after` — seconds to wait
- `anthropic-ratelimit-requests-limit` — RPM cap
- `anthropic-ratelimit-tokens-limit` — TPM cap
- `anthropic-ratelimit-tokens-remaining` — tokens left this window

**Fix:** The SDK handles 429 with automatic retry (configurable via `maxRetries`). For manual handling, see `anth-rate-limits`.

### 529 — `overloaded_error`

API is temporarily overloaded. Retry after 30-60 seconds. Not counted against rate limits.

### 500 — `api_error`

Internal server error. Retry with exponential backoff. If persistent, check [status.anthropic.com](https://status.anthropic.com).

## Quick Diagnostic Script

```bash
# 1. Check API status
curl -s https://status.anthropic.com/api/v2/status.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['status']['description'])"

# 2. Verify key format
echo $ANTHROPIC_API_KEY | grep -qE '^sk-ant-api03-' && echo "Key format OK" || echo "Key format WRONG"

# 3. Test minimal request
curl -s -w "\nHTTP %{http_code}" https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":8,"messages":[{"role":"user","content":"1+1="}]}'
```

## SDK Error Handling

```python
import anthropic

try:
    message = client.messages.create(...)
except anthropic.AuthenticationError as e:
    print(f"Auth failed: {e.status_code}")
except anthropic.RateLimitError as e:
    print(f"Rate limited. Retry after: {e.response.headers.get('retry-after')}s")
except anthropic.BadRequestError as e:
    print(f"Invalid request: {e.message}")
except anthropic.APIStatusError as e:
    print(f"API error {e.status_code}: {e.message}")
except anthropic.APIConnectionError:
    print("Network error — check connectivity")
```

## Prerequisites

- Use an API key supplied by the environment's secret manager and a workspace/model that the caller is authorized to use; never paste a key into a command, issue, or receipt.
- Have a sandbox project, a synthetic prompt such as `health-check-001`, and a request-correlation ID available for diagnosis.
- Capture only status, error type, request ID, retry metadata, and timing. Redact authorization headers, message content, tool inputs, and any provider response that could contain sensitive data.

## Instructions

1. Classify the HTTP status and provider error type before changing retry behavior. Preserve the request ID and relevant rate-limit headers in a redacted diagnostic record.
2. Reproduce with the smallest permitted request in the sandbox, using synthetic content and the approved model endpoint. Do not replay a user's original prompt unless its data handling has been approved.
3. Correct request construction for 400/401/403/404 errors; do not retry these blindly. Retry 429, 500, and 529 only with bounded exponential backoff, honoring `retry-after` when present.
4. Verify the fix with one canary request, then restore the prior configuration if error rate, scope, latency, or data-handling checks regress.
5. Close the diagnostic by deleting temporary fixtures and retaining only the redacted receipt.

## Output

Produce a diagnostic receipt containing `correlation_id`, status/error type, endpoint class, model identifier, request ID, retry decision, canary result, rollback result, and cleanup status. Include counts and timings rather than prompts, completions, tokens containing user data, credentials, or raw response bodies.

## Error Handling

- Treat malformed or missing error bodies as an unknown provider failure; use the HTTP status and request ID, then apply the safest bounded retry policy.
- Treat network timeouts as indeterminate: retry only an application-level idempotent operation and cap attempts to avoid duplicate work.
- If authentication or permission failures persist after a sandbox check, stop and rotate/re-authorize through the approved secret and workspace process; do not print or inspect the secret value.
- If a canary exposes an unexpected model, destination, retention period, or data class, open the circuit, roll back, and quarantine the receipt for operator review.

## Examples

For a sandbox probe, send `health-check-001` with a bounded `max_tokens` value, record only `status=200`, the request ID, and `content_redacted=true`, and assert that no user-data export occurred. For a 429, record `retry_after=2`, wait the provider value within a configured cap, issue at most the configured retry count, and report `recovered=true|false` without logging the prompt.

## Resources

- [Error Types Reference](https://platform.claude.com/docs/en/api/errors)
- [Rate Limits](https://platform.claude.com/docs/en/api/rate-limits)
- [API Status](https://status.anthropic.com)

## Next Steps

For comprehensive debugging, see `anth-debug-bundle`.
