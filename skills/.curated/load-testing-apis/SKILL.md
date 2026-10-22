---
name: load-testing-apis
description: 'Execute comprehensive load and stress testing to validate API performance
  and scalability.

  Use when validating API performance under load.

  Trigger with phrases like "load test the API", "stress test API", or "benchmark
  API performance".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:load-*)
version: 1.25.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- testing
- performance
- scaling
compatibility: Designed for Claude Code
---
# Load Testing APIs

## Overview

Execute comprehensive load, stress, and soak tests to validate API performance, identify bottlenecks, and establish throughput baselines. Generate test scripts for k6, Artillery, or wrk that simulate realistic traffic patterns with configurable virtual user ramp-up, request distribution, and failure threshold assertions.

## Prerequisites

- Load testing tool installed: k6 (recommended), Artillery, wrk, or Apache JMeter
- Target API deployed in a staging/performance environment (never load test production without safeguards)
- Monitoring stack accessible: Grafana/Prometheus, Datadog, or CloudWatch for correlating test results with server metrics
- API authentication credentials for testing (API keys, test user JWT tokens)
- Baseline performance SLOs defined (target p95 latency, max error rate, minimum throughput)

## Instructions

1. Read the API specification and route definitions using Glob and Read to build a complete list of endpoints, identifying high-traffic paths and resource-intensive operations.
2. Define test scenarios modeling realistic user behavior: browsing (80% reads), checkout (mixed reads + writes), and spike traffic patterns with appropriate think times between requests.
3. Generate k6 or Artillery test scripts with configurable stages: ramp-up (2 min), sustained load (10 min), spike (2 min at 3x), and cool-down (2 min).
4. Configure request distribution to match production traffic patterns -- weighted random selection across endpoints rather than uniform distribution.
5. Add threshold assertions for pass/fail criteria: p95 response time < 500ms, error rate < 1%, throughput > 100 requests/second.
6. Implement data-driven requests using CSV or JSON fixtures for realistic payloads, unique user IDs, and varied query parameters to avoid cache-only testing.
7. Execute baseline test at expected production load, then gradually increase to 2x, 5x, and 10x to identify the breaking point and saturation behavior.
8. Analyze results: correlate latency spikes with server metrics (CPU, memory, DB connections, event loop lag), identify the bottleneck (database, network, compute), and document findings.
9. Generate a performance report comparing results against SLO thresholds with recommendations for optimization.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/load-tests/scenarios/` - k6/Artillery test scripts per traffic scenario
- `${CLAUDE_SKILL_DIR}/load-tests/data/` - Test data fixtures (users, payloads, tokens)
- `${CLAUDE_SKILL_DIR}/load-tests/thresholds.json` - Pass/fail threshold configuration
- `${CLAUDE_SKILL_DIR}/reports/load-test-results.json` - Raw test results with timing data
- `${CLAUDE_SKILL_DIR}/reports/load-test-summary.md` - Human-readable performance analysis report
- `${CLAUDE_SKILL_DIR}/reports/bottleneck-analysis.md` - Identified bottlenecks with remediation recommendations

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Connection refused | Target server ran out of file descriptors or connection pool exhausted | Increase server `ulimit` and connection pool size; note the concurrent connection limit |
| Timeout spike at ramp-up | Server cannot handle connection establishment rate | Implement connection pre-warming; increase ramp-up duration; add connection pooling |
| 429 responses dominate results | Rate limiter engaging during load test | Whitelist load test source IPs in rate limiter; or test rate limiter behavior separately |
| Inconsistent baseline results | Shared staging environment with other traffic | Isolate test environment; run tests during off-hours; use dedicated performance environment |
| Memory leak detected | Soak test shows steadily increasing memory over hours | Flag for development team; identify leaking endpoint by isolating test scenarios |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**E-commerce checkout flow**: Simulate 500 concurrent users browsing products (GET, 70%), adding to cart (POST, 20%), and completing checkout (POST, 10%) with 2-5 second think times between actions.

**API spike test**: Ramp from 50 to 1000 virtual users in 30 seconds to simulate traffic spike from marketing campaign launch, verifying the auto-scaler responds and latency recovers within 60 seconds.

**Soak test for memory leaks**: Sustain 200 concurrent users for 4 hours, monitoring server memory, connection counts, and response times for degradation patterns indicating resource leaks.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- k6 documentation: https://k6.io/docs/
- Artillery documentation: https://www.artillery.io/docs
- Google SRE: Load Testing chapter
- Performance testing anti-patterns and best practices
