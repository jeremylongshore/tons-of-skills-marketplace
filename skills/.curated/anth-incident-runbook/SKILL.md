---
name: anth-incident-runbook
description: 'Execute incident response procedures for Claude API outages and degradation.

  Use when Claude API is returning errors, experiencing high latency,

  or showing degraded performance in production.

  Trigger with phrases like "anthropic incident", "claude api down",

  "anthropic outage", "claude degraded", "anthropic runbook".

  '
allowed-tools: Read, Bash(curl:*), Grep
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- ai
- anthropic
compatibility: Designed for Claude Code
---
# Anthropic Incident Runbook

## Severity Classification

| Severity | Condition | Response Time |
|----------|-----------|---------------|
| P1 | API returning 500/529 for all requests | Immediate |
| P2 | Rate limiting (429) or high latency (>10s p99) | 15 minutes |
| P3 | Intermittent errors (<5% error rate) | 1 hour |
| P4 | Degraded quality (not errors) | Next business day |

## Immediate Triage (First 5 Minutes)

```bash
# 1. Check Anthropic status page
curl -s https://status.anthropic.com/api/v2/status.json | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d['status']['indicator'], '-', d['status']['description'])"

# 2. Test API connectivity
curl -s -w "\nHTTP %{http_code} | Time: %{time_total}s\n" \
  https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-haiku-4-20250514","max_tokens":8,"messages":[{"role":"user","content":"1"}]}'

# 3. Check rate limit headers
curl -s -D - https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-haiku-4-20250514","max_tokens":8,"messages":[{"role":"user","content":"1"}]}' \
  2>/dev/null | grep -i "ratelimit\|retry-after\|request-id"
```

## Decision Tree

```
API returning errors?
├── 401/403 → Key issue → Check ANTHROPIC_API_KEY is set and valid
├── 429 → Rate limited → Check headers, reduce traffic, wait for retry-after
├── 500 → Server error → Check status.anthropic.com, retry with backoff
├── 529 → Overloaded → Temporary, retry after 30-60s
└── Timeouts → Network or long generation → Increase timeout, check max_tokens
```

## Mitigation Actions

### Rate Limiting (429)

```python
# Immediate: reduce traffic
# 1. Enable circuit breaker
# 2. Queue non-critical requests
# 3. Switch to Message Batches for bulk work
# 4. Reduce max_tokens to shorten generation time
```

### API Outage (500/529)

```python
# Graceful degradation
def get_response_with_fallback(prompt: str) -> str:
    try:
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
    except (anthropic.InternalServerError, anthropic.APIStatusError):
        return "Our AI assistant is temporarily unavailable. Please try again shortly."
```

### Key Compromise

```bash
# 1. Immediately revoke key at console.anthropic.com
# 2. Generate new key
# 3. Deploy new key to all environments
# 4. Audit recent usage for unauthorized calls
# 5. File incident report
```

## Postmortem Template

```markdown
## Incident: [Title]
- **Duration:** [start] to [end]
- **Severity:** P[1-4]
- **Impact:** [what users experienced]
- **Root Cause:** [what went wrong]
- **Detection:** [how we found out]
- **Mitigation:** [what we did to fix it]
- **Request IDs:** [from debug logs]
- **Action Items:**
  - [ ] [preventive measure 1]
  - [ ] [preventive measure 2]
```

## Error Handling

| Symptom | Likely Cause | Quick Fix |
|---------|-------------|-----------|
| All requests fail 401 | Key rotated/expired | Check Console for active keys |
| Sudden 429 spike | Traffic burst or tier change | Check rate limit headers |
| Slow responses (>10s) | Large max_tokens or complex prompt | Reduce max_tokens, use Haiku |
| Intermittent 500s | Upstream API issue | Check status.anthropic.com |

## Overview

This runbook provides a bounded, evidence-driven response to Claude API outages, throttling, latency, key compromise, and degraded behavior. It separates provider diagnosis from application containment and requires a reversible change for every mitigation.

## Prerequisites

- Maintain on-call ownership, escalation contacts, status-page access, a sandbox health probe, circuit-breaker/fallback controls, and a tested rollback path.
- Keep environment-specific keys in a secret manager with least privilege and documented revocation authority. Do not place credentials in incident chat or tickets.
- Configure redacted telemetry for status class, request ID, model class, latency, rate-limit headers, aggregate impact, and change history; exclude prompts, completions, PII, tool arguments, and key material.

## Instructions

1. Declare severity from observed scope, record a correlation ID, and verify the issue with a synthetic sandbox probe before changing production traffic.
2. Check provider status, request IDs, rate-limit metadata, application error/latency aggregates, and recent deploys. Distinguish provider failure from key, permission, network, or request-shape failure.
3. Contain with the narrowest reversible control: reduce traffic, open the circuit, queue noncritical work, or use an already approved fallback. Preserve authorization and retention rules during degradation.
4. For a suspected key compromise, revoke through the secret manager/provider console, rotate, deploy to one canary, verify, and then revoke the old credential. Avoid exposing the key while testing.
5. Confirm recovery with synthetic probes and aggregate production metrics, then roll back emergency configuration if it caused scope, quality, cost, or data-handling regressions. Capture a redacted postmortem and clean temporary artifacts.

## Output

Produce an incident receipt with severity, start/end times, affected scope, status/error classes, aggregate request impact, mitigation and owner, provider/request IDs, canary and recovery evidence, rollback/revocation reference, follow-up actions, and retention status. Never include raw content or credentials.

## Examples

For a synthetic 529 spike, record `severity=P1; probe=529; circuit=open; noncritical_queued=true; fallback=approved-static; side_effects=0`, then perform one bounded half-open probe after the configured interval. If it passes, canary recovery and record `rollback=ready; cleanup=verified`; otherwise keep the circuit open and escalate.

## Resources

- [API Status](https://status.anthropic.com)
- [Error Reference](https://platform.claude.com/docs/en/api/errors)
- [Rate Limits](https://platform.claude.com/docs/en/api/rate-limits)

## Next Steps

For data compliance, see `anth-data-handling`.
