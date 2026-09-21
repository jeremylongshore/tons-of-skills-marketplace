---
name: anth-observability
description: 'Set up observability for Claude API integrations with metrics, logging,

  and alerting for latency, cost, errors, and token usage.

  Trigger with phrases like "anthropic monitoring", "claude observability",

  "anthropic metrics", "track claude usage", "claude dashboard".

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
# Anthropic Observability

## Overview

Instrument Claude API calls with structured logging, Prometheus metrics, and cost tracking. Every API response includes `usage` data and rate limit headers — capture these for dashboards and alerting.

## Structured Logging

```python
import anthropic
import logging
import time
import json

logger = logging.getLogger("claude")

def create_with_logging(client: anthropic.Anthropic, **kwargs) -> anthropic.types.Message:
    start = time.monotonic()
    request_meta = {
        "model": kwargs.get("model"),
        "max_tokens": kwargs.get("max_tokens"),
        "tool_count": len(kwargs.get("tools", [])),
        "stream": kwargs.get("stream", False),
    }

    try:
        response = client.messages.create(**kwargs)
        duration_ms = int((time.monotonic() - start) * 1000)

        logger.info(json.dumps({
            "event": "claude.request",
            "request_id": response._request_id,
            "model": response.model,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "cache_read_tokens": getattr(response.usage, "cache_read_input_tokens", 0),
            "stop_reason": response.stop_reason,
            "duration_ms": duration_ms,
            "content_blocks": len(response.content),
        }))
        return response

    except anthropic.APIStatusError as e:
        duration_ms = int((time.monotonic() - start) * 1000)
        logger.error(json.dumps({
            "event": "claude.error",
            "status": e.status_code,
            "error_type": getattr(e, "type", "unknown"),
            "duration_ms": duration_ms,
            "request_id": e.response.headers.get("request-id", "unknown"),
        }))
        raise
```

## Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

claude_requests = Counter(
    "claude_requests_total", "Total Claude API requests",
    ["model", "stop_reason", "status"]
)
claude_latency = Histogram(
    "claude_latency_seconds", "Claude API latency",
    ["model"], buckets=[0.5, 1, 2, 5, 10, 30, 60]
)
claude_tokens = Counter(
    "claude_tokens_total", "Token usage",
    ["model", "direction"]  # direction: input|output|cache_read
)
claude_cost = Counter(
    "claude_cost_usd", "Estimated cost in USD",
    ["model"]
)
claude_rate_limit_remaining = Gauge(
    "claude_rate_limit_remaining", "Remaining rate limit",
    ["dimension"]  # dimension: requests|tokens
)

def track_metrics(response, duration: float):
    model = response.model
    claude_requests.labels(model=model, stop_reason=response.stop_reason, status="ok").inc()
    claude_latency.labels(model=model).observe(duration)
    claude_tokens.labels(model=model, direction="input").inc(response.usage.input_tokens)
    claude_tokens.labels(model=model, direction="output").inc(response.usage.output_tokens)

    # Cost estimation
    pricing = {"claude-haiku-4-20250514": (0.80, 4.0), "claude-sonnet-4-20250514": (3.0, 15.0)}
    rates = pricing.get(model, (3.0, 15.0))
    cost = (response.usage.input_tokens * rates[0] + response.usage.output_tokens * rates[1]) / 1e6
    claude_cost.labels(model=model).inc(cost)
```

## Key Metrics Dashboard

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `claude_requests_total{status="error"}` | Error count | > 5% of total |
| `claude_latency_seconds` p99 | Tail latency | > 10s |
| `claude_cost_usd` daily | Daily spend | > 80% budget |
| `claude_rate_limit_remaining{dimension="requests"}` | RPM headroom | < 10% remaining |
| `claude_tokens_total{direction="output"}` rate | Output throughput | Spike detection |

## Usage API (Server-Side)

```python
# Anthropic's Usage & Cost API for billing reconciliation
# GET https://api.anthropic.com/v1/usage
# Returns daily token usage and cost per model
```

## Error Handling

| Observability Gap | Risk | Fix |
|-------------------|------|-----|
| No request_id logged | Can't debug with support | Capture `response._request_id` |
| Missing cost tracking | Budget surprise | Track per-request cost |
| No latency histogram | Can't spot slow queries | Add Prometheus/Datadog histograms |

## Prerequisites

- Define SLOs, alert owners, budget and rate-limit thresholds, approved metric labels, and retention rules for telemetry.
- Configure authenticated server-side access through a secret manager and use a sandbox workspace with synthetic requests to verify instrumentation.
- Establish a redaction/filter policy before enabling logs, traces, dashboards, or usage reconciliation; prompts, responses, secrets, and personal data are never telemetry fields.

## Instructions

1. Instrument the request boundary with request ID, model, status, stop reason, token aggregates, cache counters, and duration while excluding content and high-cardinality identifiers.
2. Emit success and failure metrics for authentication, 4xx/5xx, 429, timeout, latency, spend, and remaining rate-limit headroom. Validate labels against an allowlist and cap cardinality.
3. Test dashboards and alerts with synthetic success, timeout, rate-limit, permission, and malformed-response fixtures. Verify the alert path without sending live customer data.
4. Reconcile usage through the approved authenticated server-side API on a bounded schedule, compare aggregate totals, and alert on unexplained divergence or budget breach.
5. Canary telemetry changes, then promote with owner approval. If redaction, cardinality, or retention checks fail, disable the new sink, restore the prior configuration, and preserve only a redacted receipt.

## Output

Produce an observability receipt containing instrumentation version, metric/label allowlist, synthetic test results, alert thresholds, aggregate usage/cost/latency/error outcomes, retention policy, canary scope, approval, and rollback reference. Exclude prompts, responses, API keys, user IDs, and raw exception bodies.

## Examples

Send synthetic `fixture-request-001` through a staging client and assert `request_id_present=1; content_fields=0; labels_allowlisted=1`; inject a synthetic 429 and verify the alert fires. Record `telemetry=pass; retention=24h; rollback=metrics-v1` without recording the fixture text.

## Resources

- [Usage & Cost API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api)
- [Rate Limits](https://platform.claude.com/docs/en/api/rate-limits)
- [API Status](https://status.anthropic.com)

## Next Steps

For incident response, see `anth-incident-runbook`.
