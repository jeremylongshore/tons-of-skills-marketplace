---
name: clade-incident-runbook
description: "Respond to Anthropic API incidents \u2014 outages, degraded performance,\n\
  Use when working with incident-runbook patterns.\nerror spikes, and rate limit issues\
  \ in production.\nTrigger with \"anthropic down\", \"claude outage\", \"anthropic\
  \ incident\",\n\"claude not responding\", \"anthropic 529\".\n"
allowed-tools: Read, Grep, Bash(curl:*)
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- incident
- runbook
compatibility: Designed for Claude Code
---
# Anthropic Incident Runbook

## Overview

Respond to Anthropic API incidents in production — outages, sustained 529 errors, authentication failures, and timeouts. Covers status page checking, severity classification, model fallback activation, communication, and post-incident review.

## Step 1: Confirm the Issue

```bash
# Check Anthropic status
curl -s https://status.anthropic.com/api/v2/status.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(f\"Status: {d['status']['description']} ({d['status']['indicator']})\")"

# Test API directly
curl -s -w "\nHTTP %{http_code} in %{time_total}s\n" \
  https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "claude-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-haiku-4-5-20251001","max_tokens":5,"messages":[{"role":"user","content":"ping"}]}'
```

## Step 2: Classify Severity

| Symptom | Severity | Action |
|---------|----------|--------|
| 529 overloaded (intermittent) | Low | SDK auto-retries handle this |
| 529 overloaded (sustained 5+ min) | Medium | Switch to fallback model |
| 401/403 on all requests | High | API key issue — check console |
| All requests timing out | High | Check status page, activate fallback |
| Status page shows incident | Varies | Follow status page updates |

## Step 3: Activate Fallback

```typescript
async function callWithFallback(params: Anthropic.MessageCreateParams) {
  try {
    return await client.messages.create(params);
  } catch (err) {
    if (err instanceof Anthropic.APIError && (err.status === 529 || err.status === 500)) {
      // Try a different model
      if (params.model.includes('opus')) {
        return await client.messages.create({ ...params, model: 'claude-sonnet-4-20250514' });
      }
      if (params.model.includes('sonnet')) {
        return await client.messages.create({ ...params, model: 'claude-haiku-4-5-20251001' });
      }
    }
    throw err;
  }
}
```

## Step 4: Communicate

- Update your status page if user-facing
- Note: Anthropic incidents typically resolve in 15-60 minutes

## Step 5: Post-Incident

- Check your error logs for the incident window
- Calculate impact (failed requests, user impact)
- Verify all systems recovered

## Output

- Incident confirmed via status page and direct API test
- Severity classified (Low/Medium/High) based on symptoms
- Fallback activated if needed (downgrade model or queue requests)
- Impact assessed and documented post-incident

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| API Error | Check error type and status code | See `clade-common-errors` |

## Examples

See Step 1 (curl status check and API test), Step 2 (severity classification table), Step 3 (fallback code with model downgrade), and Step 5 (post-incident checklist) above.

## Resources

- [Anthropic Status](https://status.anthropic.com)
- [Status API](https://status.anthropic.com/api)

## Next Steps

See `clade-reliability-patterns` for building resilient integrations.

## Prerequisites

- Production Claude integration deployed
- Fallback model configuration in place (see `clade-reliability-patterns`)
- Monitoring/alerting configured (see `clade-observability`)

## Instructions

### Step 1: Review the patterns below

Each section contains production-ready code examples. Copy and adapt them to your use case.

### Step 2: Apply to your codebase

Integrate the patterns that match your requirements. Test each change individually.

### Step 3: Verify

Run your test suite to confirm the integration works correctly.
