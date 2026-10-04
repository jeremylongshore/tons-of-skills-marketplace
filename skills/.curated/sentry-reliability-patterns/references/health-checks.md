# Health Checks

## Sentry Health Check Endpoint

```typescript
// routes/health.ts
import * as Sentry from '@sentry/node';
import { sentryBreaker } from '../lib/sentry-circuit-breaker';

app.get('/health/sentry', async (_req, res) => {
  const client = Sentry.getClient();
  const circuit = sentryBreaker.getStatus();

  if (!client) {
    return res.status(503).json({
      status: 'unhealthy',
      error: 'Sentry client not initialized',
      circuit,
    });
  }

  // Send a probe message and check if it flushes
  try {
    Sentry.captureMessage('health-check-probe', 'debug');
    const flushed = await Sentry.flush(3000);

    res.json({
      status: flushed ? 'healthy' : 'degraded',
      sdk_version: Sentry.SDK_VERSION,
      environment: client.getOptions().environment,
      release: client.getOptions().release,
      flush_ok: flushed,
      circuit,
    });
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      error: error instanceof Error ? error.message : String(error),
      circuit,
    });
  }
});
```

## Response Schema

Healthy response:

```json
{
  "status": "healthy",
  "sdk_version": "8.x.x",
  "environment": "production",
  "release": "abc123",
  "flush_ok": true,
  "circuit": { "state": "closed", "failures": 0, "lastFailureAt": 0 }
}
```

Degraded response (flush timed out but SDK running):

```json
{
  "status": "degraded",
  "sdk_version": "8.x.x",
  "flush_ok": false,
  "circuit": { "state": "half-open", "failures": 3, "lastFailureAt": 1711100400000 }
}
```

Unhealthy response (SDK not initialized or Sentry unreachable):

```json
{
  "status": "unhealthy",
  "error": "Sentry client not initialized",
  "circuit": { "state": "open", "failures": 5, "lastFailureAt": 1711100400000 }
}
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io)*
