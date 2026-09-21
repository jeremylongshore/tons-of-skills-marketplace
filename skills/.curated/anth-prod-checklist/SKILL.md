---
name: anth-prod-checklist
description: 'Execute production deployment checklist for Claude API integrations.

  Use when deploying Claude-powered features to production,

  preparing for launch, or implementing go-live validation.

  Trigger with phrases like "anthropic production", "deploy claude",

  "claude go-live", "anthropic launch checklist", "production ready claude".

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
# Anthropic Production Checklist

## Overview

Complete checklist for deploying Claude API integrations to production with reliability, observability, and cost controls.

## Pre-Launch Checklist

### Authentication & Keys

- [ ] Production API key from dedicated Workspace
- [ ] Key stored in secret manager (not env files on servers)
- [ ] Key rotation procedure documented and tested
- [ ] Separate keys for each environment (dev/staging/prod)

### Error Handling

- [ ] All 5 error types handled: `authentication_error`, `invalid_request_error`, `rate_limit_error`, `api_error`, `overloaded_error`
- [ ] SDK `maxRetries` set (recommended: 3-5 for production)
- [ ] Custom error logging with `request-id` captured
- [ ] Circuit breaker for sustained API failures

### Rate Limits & Cost

- [ ] Usage tier verified at [console.anthropic.com](https://console.anthropic.com/settings/limits)
- [ ] Application-level rate limiting implemented
- [ ] Cost alerts configured (monthly spend caps)
- [ ] Model selection optimized (Haiku for simple tasks, Sonnet for complex)
- [ ] `max_tokens` set to realistic values (not inflated)
- [ ] Prompt caching enabled for repeated system prompts

### Reliability

- [ ] Timeout configured (`timeout` parameter, recommended 60-120s)
- [ ] Graceful degradation when API is unavailable
- [ ] Health check endpoint tests API connectivity

```python
async def health_check():
    try:
        # Use token counting as a cheap health probe (no generation cost)
        count = client.messages.count_tokens(
            model="claude-haiku-4-20250514",
            messages=[{"role": "user", "content": "ping"}]
        )
        return {"status": "healthy", "tokens": count.input_tokens}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}
```

### Observability

- [ ] Request/response logging (redact content, keep metadata)
- [ ] Latency tracking (p50, p95, p99)
- [ ] Token usage tracking (input + output per request)
- [ ] Cost tracking per feature/customer
- [ ] Error rate alerting (429s, 5xx, timeouts)

```python
import logging
import time

logger = logging.getLogger("anthropic")

def tracked_create(**kwargs):
    start = time.monotonic()
    try:
        response = client.messages.create(**kwargs)
        duration = time.monotonic() - start
        logger.info(
            "claude_request",
            extra={
                "request_id": response._request_id,
                "model": response.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "duration_ms": int(duration * 1000),
                "stop_reason": response.stop_reason,
            }
        )
        return response
    except Exception as e:
        duration = time.monotonic() - start
        logger.error("claude_error", extra={"error": str(e), "duration_ms": int(duration * 1000)})
        raise
```

### Content Safety

- [ ] System prompts reviewed for injection resistance
- [ ] User input validated and length-limited
- [ ] Output scanned for sensitive data leakage
- [ ] Content moderation for user-facing responses

### Infrastructure

- [ ] Deployment uses canary/rolling strategy
- [ ] Rollback procedure documented and tested
- [ ] Runbook created (see `anth-incident-runbook`)
- [ ] On-call escalation path defined

## Alerting Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Error rate (5xx) | > 1% | > 5% |
| p99 latency | > 10s | > 30s |
| 429 rate | > 5/min | > 20/min |
| Daily cost | > 80% budget | > 100% budget |
| Auth failures (401/403) | > 0 | > 0 (immediate) |

## Prerequisites

- Have an approved release/artifact digest, production workspace, secret-manager reference, owner/on-call, change record, canary plan, and tested rollback command.
- Define the model/version, data classification, allowed destinations, retention, budget, rate-limit, latency, error, and content-safety thresholds for this release.
- Prepare synthetic fixtures and a staging environment that matches production policy; never validate readiness with live customer content or by printing credentials.

## Instructions

1. Confirm every checklist item with an evidence link or redacted receipt: authentication, workspace isolation, model/version, error handling, limits, cost, observability, content safety, and rollback.
2. Run staging contract, health, synthetic redaction, timeout, rate-limit, permission, and output-safety tests. Verify logs/metrics contain metadata only and that deletion/retention behavior is proven.
3. Deploy the approved artifact to a small internal canary. Monitor p95/p99 latency, 4xx/5xx/429, token/cost aggregates, rate-limit headroom, and policy probes; halt on any critical threshold.
4. Require owner and on-call approval before staged production promotion. Preserve the prior revision and ensure the rollback path is executable without exposing secrets or content.
5. After rollout, issue a redacted receipt, revoke temporary test access, and retain only the evidence required by the documented policy.

## Output

Produce a go-live receipt containing artifact/config digests, workspace/model classes, checklist evidence, synthetic test results, canary and threshold outcomes, approvals, rollout state, retention cleanup, and rollback reference. Exclude API keys, prompts, responses, customer identifiers, and raw exception text.

## Error Handling

| Gate failure | Required response |
|---|---|
| Authentication, workspace, or permission check fails | Do not deploy; verify secret binding and scope, then rotate/revoke only through the approved process. |
| 429/5xx, timeout, latency, or budget threshold fails | Halt promotion, apply bounded degradation/circuit breaking, and roll back to the prior revision. |
| Redaction, content-safety, or retention check fails | Stop traffic, quarantine affected artifacts, correct the boundary, and rerun staging evidence. |
| Missing approval or unverifiable evidence | Mark release not ready; do not bypass the gate. |

## Examples

For `artifact=sha256:fixture` in staging, run synthetic `fixture-request-001`, assert `sensitive_content_logged=0; contacts_exported=0; rollback_test=pass`, then canary 1% internal traffic. A failed 429 gate records `go_live=halted; rollback=prior-revision` and sends no further production traffic.

## Resources

- [API Status](https://status.anthropic.com)
- [Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [Rate Limits](https://platform.claude.com/docs/en/api/rate-limits)

## Next Steps

For version upgrades, see `anth-upgrade-migration`.
