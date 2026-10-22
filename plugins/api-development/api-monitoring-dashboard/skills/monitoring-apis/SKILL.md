---
name: monitoring-apis
description: 'Build real-time API monitoring dashboards with metrics, alerts, and
  health checks.

  Use when tracking API health and performance metrics.

  Trigger with phrases like "monitor the API", "add API metrics", or "setup API monitoring".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:monitor-*)
version: 1.26.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- monitoring
- performance
- dashboard
compatibility: Designed for Claude Code
---
# Monitoring APIs

## Overview

Build real-time API monitoring with metrics collection (request rate, latency percentiles, error rates), health check endpoints, and alerting rules. Instrument API middleware to emit Prometheus metrics or StatsD counters, configure Grafana dashboards with SLO tracking, and implement synthetic monitoring probes for uptime verification.

## Prerequisites

- Prometheus + Grafana stack, or Datadog/New Relic/CloudWatch for metrics and dashboards
- Metrics client library: `prom-client` (Node.js), `prometheus_client` (Python), or Micrometer (Java)
- Alerting channel configured: PagerDuty, Slack webhook, or email for alert routing
- Structured logging library: Winston, Pino (Node.js), structlog (Python), or Logback (Java)
- Synthetic monitoring tool: Checkly, Uptime Robot, or custom cron-based health probes

## Instructions

1. Examine existing middleware and logging setup using Grep and Read to identify current observability coverage and gaps.
2. Implement metrics middleware that records per-request data: `http_request_duration_seconds` histogram (with method, path, status labels), `http_requests_total` counter, and `http_requests_in_flight` gauge.
3. Create a `/health` endpoint returning structured health status including dependency checks (database connectivity, cache availability, external service reachability) with response time for each.
4. Add a `/ready` endpoint separate from health that returns 503 during startup initialization and graceful shutdown, for load balancer integration.
5. Configure histogram buckets aligned with SLO targets: [0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10] seconds for comprehensive latency distribution.
6. Build Grafana dashboard panels: request rate (QPS), p50/p95/p99 latency, error rate percentage, active connections, and per-endpoint breakdown.
7. Define alerting rules: error rate > 5% for 5 minutes (critical), p99 latency > 2s for 10 minutes (warning), health check failure for 3 consecutive probes (critical).
8. Implement synthetic monitoring that sends periodic requests to critical endpoints from external locations, measuring availability and latency from the consumer perspective.
9. Add SLO tracking with error budget calculation: define SLO (99.9% availability, p95 < 500ms), compute burn rate, and alert when error budget consumption exceeds projected pace.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/src/middleware/metrics.js` - Prometheus metrics collection middleware
- `${CLAUDE_SKILL_DIR}/src/routes/health.js` - Health check and readiness endpoints
- `${CLAUDE_SKILL_DIR}/monitoring/dashboards/` - Grafana dashboard JSON definitions
- `${CLAUDE_SKILL_DIR}/monitoring/alerts/` - Alerting rule definitions (Prometheus AlertManager or Grafana)
- `${CLAUDE_SKILL_DIR}/monitoring/synthetic/` - Synthetic monitoring probe scripts
- `${CLAUDE_SKILL_DIR}/monitoring/slo.yaml` - SLO definitions and error budget configuration

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Metrics cardinality explosion | High-cardinality labels (user ID, request ID) on metrics | Use bounded label values only (method, status code, endpoint group); aggregate user-level data in logs |
| Health check false positive | Health endpoint returns 200 but dependent service is degraded | Include dependency checks with individual status; use structured response with `degraded` state |
| Alert fatigue | Too many low-severity alerts firing during normal operations | Tune alert thresholds using historical baselines; implement alert grouping and deduplication |
| Dashboard data gap | Metrics not collected during deployment rollout window | Configure Prometheus scrape interval < deployment duration; use push-based metrics during deploys |
| SLO miscalculation | Error budget calculation uses wrong time window or includes planned maintenance | Exclude maintenance windows from SLO calculation; align window with business reporting period |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**RED method dashboard**: Request rate, Error rate, and Duration panels per endpoint, with drill-down from overview to individual endpoint detail, including top-10 slowest endpoints by p99.

**SLO-based alerting**: Define 99.9% availability SLO with 30-day rolling window, alert when 1-hour burn rate exceeds 14.4x (consuming daily error budget in 1 hour), with PagerDuty escalation.

**Dependency health matrix**: Dashboard showing real-time health status of all downstream dependencies (database, cache, external APIs) with latency sparklines and circuit breaker state indicators.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- Google SRE Book: Monitoring Distributed Systems chapter
- Prometheus documentation: https://prometheus.io/docs/
- Grafana dashboards: https://grafana.com/docs/grafana/latest/
- USE Method and RED Method for metrics design
