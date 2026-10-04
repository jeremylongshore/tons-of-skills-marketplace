# Error Handling Reference

## Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| App crashes on `Sentry.init()` | Invalid DSN, network error, or SDK bug | Wrap in try/catch via `initSentrySafe()`; set `sentryAvailable = false` |
| Events lost on `SIGTERM` / deploy | No `Sentry.close()` before `process.exit()` | Register `SIGTERM`/`SIGINT` handlers calling `Sentry.close(2000)` |
| Sentry outage cascades latency | Every error path blocks on HTTP to Sentry | Circuit breaker trips after 5 failures, skips sends for 60s |
| Events lost during network blip | SDK silently drops events with no retry | Use `makeRetryTransport` with exponential backoff + offline queue |
| Silent event loss, no alerts | Sentry SDK fails without throwing | Health check endpoint probes with `captureMessage` + `flush` |
| Queue file grows unbounded | Never drained or Sentry permanently down | Cap at `MAX_QUEUED_EVENTS` (1000); call `drainQueue()` on startup |
| `beforeSend` hook crashes pipeline | User-supplied callback throws | Wrap in nested try/catch, return raw event on failure |
| Corrupt offline queue file | Partial write or disk error | Parse in try/catch, delete corrupt file, log warning |
| Client not created after init | DSN is empty string or malformed | Check `Sentry.getClient()` after init; log warning if null |
| Events queued but never replayed | `drainQueue()` only called at startup | Add periodic drain via `setInterval` or cron |

## Diagnostic Checklist

1. **Check initialization**: Call `Sentry.getClient()` — if null, DSN is invalid or init was skipped
2. **Check circuit state**: Call `sentryBreaker.getStatus()` — if open, Sentry was unreachable
3. **Check offline queue**: Look for queue file at `SENTRY_QUEUE_PATH` — if present, events are buffered
4. **Check flush result**: `Sentry.flush(timeout)` returns false if timeout expired before all events sent
5. **Check SDK transport**: Network errors appear in custom transport catch blocks

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io)*
