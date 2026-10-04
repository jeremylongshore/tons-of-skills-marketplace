# Examples

## TypeScript — Full Integration

Complete production entrypoint wiring all three reliability patterns together.

```typescript
// app.ts — production entrypoint with all reliability patterns
import { initSentrySafe } from './lib/sentry-safe';
import { sentryBreaker } from './lib/sentry-circuit-breaker';
import { drainQueue } from './lib/sentry-offline-queue';
import { registerShutdownHandlers } from './lib/sentry-shutdown';
import { makeRetryTransport } from './lib/sentry-transport';
import express from 'express';

// 1. Initialize Sentry with resilient transport
initSentrySafe(process.env.SENTRY_DSN ?? '', {
  environment: process.env.NODE_ENV ?? 'production',
  release: process.env.RELEASE_SHA,
  tracesSampleRate: 0.2,
  transport: makeRetryTransport,
});

// 2. Drain any events queued from a previous crash or outage
drainQueue().then((count) => {
  if (count > 0) console.log(`Replayed ${count} offline events`);
}).catch(console.error);

// 3. Register shutdown handlers
const app = express();
const server = app.listen(3000);

registerShutdownHandlers(async () => {
  server.close();
  // Close DB connections, etc.
});

// 4. Use circuit breaker for all error capture
app.use((err: Error, req: express.Request, res: express.Response, _next: express.NextFunction) => {
  sentryBreaker.captureException(err, {
    url: req.originalUrl,
    method: req.method,
  });
  res.status(500).json({ error: 'Internal server error' });
});
```

## Python — Full Integration

Complete Python application with all three patterns.

```python
# main.py — production entrypoint
import os
from sentry_reliable import (
    init_sentry_safe,
    breaker,
    drain_queue,
)

# 1. Initialize with graceful degradation
init_sentry_safe(os.getenv("SENTRY_DSN", ""))

# 2. Drain offline queue from previous crash
drained = drain_queue()
if drained:
    print(f"Replayed {drained} offline events")

# 3. Use circuit breaker for all error capture
def handle_request(request):
    try:
        return process(request)
    except Exception as e:
        breaker.capture_exception(e, {"path": request.path})
        raise
```

## Example: Verifying Circuit Breaker Behavior

```typescript
// test/circuit-breaker.test.ts
import { sentryBreaker } from '../lib/sentry-circuit-breaker';

// Simulate 5 failures to trip the circuit open
for (let i = 0; i < 5; i++) {
  sentryBreaker.captureException(new Error(`Failure ${i + 1}`));
}

console.log(sentryBreaker.getStatus());
// { state: 'open', failures: 5, lastFailureAt: 1711100400000 }

// After cooldown period, circuit enters half-open and probes
// A successful probe resets to closed
```

## Example: Request-Level Error Handling

```typescript
import { captureError } from './lib/sentry-safe';

app.get('/api/data', async (req, res) => {
  try {
    const data = await fetchData(req.query.id);
    res.json(data);
  } catch (error) {
    // captureError handles fallback automatically
    const eventId = captureError(error as Error, {
      endpoint: '/api/data',
      query: req.query,
      userId: req.user?.id,
    });

    res.status(500).json({
      error: 'Internal server error',
      eventId, // undefined if Sentry was unavailable
    });
  }
});
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io)*
