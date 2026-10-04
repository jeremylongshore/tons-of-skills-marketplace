---
name: sentry-reliability-patterns
description: 'Build reliable Sentry integrations with graceful degradation, circuit
  breakers, and offline queuing.

  Use when implementing fault-tolerant error tracking, handling SDK initialization
  failures,

  building retry logic for Sentry transports, or ensuring apps survive Sentry outages.

  Trigger with "sentry reliability", "sentry circuit breaker", "sentry offline queue",

  "sentry graceful degradation", "sentry failover", or "resilient sentry setup".

  '
allowed-tools: Read, Write, Edit, Grep, Bash(node:*), Bash(pip:*), Bash(python*:*)
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- reliability
- resilience
- circuit-breaker
- offline-queue
- graceful-degradation
compatibility: Designed for Claude Code
---
# Sentry Reliability Patterns

## Overview

Build Sentry integrations that never take your application down via three pillars: safe initialization with graceful degradation, a circuit breaker that stops hammering Sentry when unreachable, and an offline event queue that buffers errors during outages. Every pattern prioritizes application uptime over telemetry completeness.

## Prerequisites

- `@sentry/node` v8+ (TypeScript) or `sentry-sdk` v2+ (Python)
- A valid Sentry DSN from project settings at `sentry.io`
- A fallback logging destination decided (console, file, or external logger)
- Understanding of your application shutdown lifecycle (signal handlers, container orchestration)

## Instructions

### Step 1 — Safe Initialization with Graceful Degradation

Wrap `Sentry.init()` in try/catch so an invalid DSN, network error, or SDK bug never crashes the app. Track initialization state with a boolean flag. Protect `beforeSend` callbacks with their own error boundary.

Create `lib/sentry-safe.ts` with `initSentrySafe()` and `captureError()`. See [graceful-degradation.md](references/graceful-degradation.md) for full implementation.

Key rules:

- Never let `Sentry.init()` crash the process — wrap in try/catch, set `sentryAvailable = false` on failure
- Verify client creation with `Sentry.getClient()` — invalid DSNs silently produce no client
- Always log errors locally as baseline before attempting Sentry capture
- Wrap user-supplied `beforeSend` hooks in nested try/catch — return raw event on hook failure

### Step 2 — Circuit Breaker for Sentry Outages

When Sentry is unreachable, continued attempts waste resources and add latency. Track consecutive failures and trip open after a threshold. After cooldown, enter half-open state and send a single probe.

Implement `SentryCircuitBreaker` class with closed/open/half-open states. See [circuit-breaker-pattern.md](references/circuit-breaker-pattern.md) for full implementation. Expose state via [health-checks.md](references/health-checks.md) endpoint.

Key rules:

- Default: 5 failures to trip open, 60-second cooldown before half-open probe
- In open state, skip Sentry calls entirely and log to fallback
- On half-open success, reset to closed with zero failure count
- Expose `getStatus()` for health check endpoints and monitoring dashboards

### Step 3 — Offline Queue, Custom Transport, and Graceful Shutdown

Buffer events when network is unavailable and replay on reconnect. Use bounded file-based queue to survive restarts. Pair with signal handlers that flush via `Sentry.close()` before process exit.

Implement three modules:

- `lib/sentry-offline-queue.ts` — `enqueueEvent()` and `drainQueue()`. See [network-failure-handling.md](references/network-failure-handling.md)
- `lib/sentry-transport.ts` — Custom transport with exponential backoff retry. See [timeout-handling.md](references/timeout-handling.md)
- `lib/sentry-shutdown.ts` — `SIGTERM`/`SIGINT` handlers calling `Sentry.close(2000)`. See [timeout-handling.md](references/timeout-handling.md)

Key rules:

- Cap offline queue at 1000 events, evict oldest when full
- Drain queue on startup and when connectivity restores
- Call `Sentry.close(timeout)` before `process.exit()` — without it, in-flight events are silently dropped
- For critical errors, use [dual-write-pattern.md](references/dual-write-pattern.md) to send to multiple destinations via `Promise.allSettled`

## Output

- Safe init wrapper catching SDK failures, starting app in degraded mode
- `captureError()` with automatic fallback to local logging
- Circuit breaker stopping sends after repeated failures, self-healing after cooldown
- Health check endpoint exposing SDK status and circuit breaker state
- File-based offline queue buffering events during outages, draining on reconnect
- Signal handlers flushing in-flight events before process exit
- Custom transport with exponential-backoff retry logic

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| App crashes on `Sentry.init()` | Invalid DSN or SDK bug | Wrap in try/catch via `initSentrySafe()` |
| Events lost on `SIGTERM` | No `Sentry.close()` before exit | Register signal handlers with `Sentry.close(2000)` |
| Sentry outage cascades latency | Every error path hits Sentry HTTP | Circuit breaker trips after 5 failures |
| Events lost during network blip | SDK drops events silently | Retry transport + offline queue |
| Silent event loss | SDK fails without throwing | Health check probes with `captureMessage` + `flush` |
| Queue grows unbounded | Never drained, Sentry permanently down | Cap at 1000 events, drain on startup |
| `beforeSend` crashes pipeline | User hook throws | Nested try/catch, return raw event |

See [errors.md](references/errors.md) for extended troubleshooting.

## Examples

See [examples.md](references/examples.md) for complete TypeScript and Python integration examples including full-stack wiring of all three patterns.

## Resources

- [Sentry JS Configuration](https://docs.sentry.io/platforms/javascript/configuration/) — `beforeSend`, `sampleRate`, init options
- [Custom Transports](https://docs.sentry.io/platforms/javascript/configuration/transports/) — retry and offline transports
- [Shutdown & Draining](https://docs.sentry.io/platforms/javascript/configuration/draining/) — `Sentry.close()` and `Sentry.flush()`
- [Sentry Python SDK](https://docs.sentry.io/platforms/python/) — `sentry_sdk.init()`, `flush()`, scope management
- [Sentry Status Page](https://status.sentry.io/) — monitor platform outages

## Next Steps

- Emit circuit breaker state changes to observability platform (Datadog, Prometheus) for outage alerting
- Set up periodic `drainQueue()` via `setInterval` (Node) or cron (Python) instead of startup-only
- Apply retry transport pattern to Python via `sentry_sdk.init(transport=...)` parameter
- Test failure modes in staging — simulate Sentry failures with `beforeSend` to verify circuit breaker behavior
- Add [dual-write](references/dual-write-pattern.md) for P0/fatal errors to secondary destinations (CloudWatch, PagerDuty)
