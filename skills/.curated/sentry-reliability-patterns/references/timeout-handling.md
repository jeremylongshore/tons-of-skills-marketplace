# Timeout Handling

## Custom Transport with Retry Logic

```typescript
// lib/sentry-transport.ts — resilient transport with exponential backoff
import * as Sentry from '@sentry/node';

export function makeRetryTransport(
  options: Sentry.NodeTransportOptions,
): Sentry.Transport {
  const baseTransport = Sentry.makeNodeTransport(options);

  return {
    send: async (envelope) => {
      const maxRetries = 3;
      let lastError: unknown;

      for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
          return await baseTransport.send(envelope);
        } catch (error) {
          lastError = error;
          if (attempt < maxRetries) {
            // Exponential backoff: 1s, 2s, 4s (capped at 5s)
            const delay = Math.min(1000 * Math.pow(2, attempt - 1), 5000);
            await new Promise((r) => setTimeout(r, delay));
          }
        }
      }

      // All retries exhausted — queue for offline replay
      console.error('[Sentry Transport] All retries failed:', lastError);
      return { statusCode: 0 };
    },
    flush: (timeout) => baseTransport.flush(timeout),
  };
}

// Usage in init:
// initSentrySafe(dsn, { transport: makeRetryTransport });
```

## Capture with Timeout Wrapper

```typescript
async function captureWithTimeout(
  error: Error,
  timeoutMs = 5000,
): Promise<string | null> {
  return new Promise((resolve) => {
    const timeout = setTimeout(() => {
      console.warn('[Sentry] Capture timed out');
      resolve(null);
    }, timeoutMs);

    const eventId = Sentry.captureException(error);

    Sentry.flush(timeoutMs - 100).finally(() => {
      clearTimeout(timeout);
      resolve(eventId);
    });
  });
}
```

## Graceful Shutdown with Sentry.close()

```typescript
// lib/sentry-shutdown.ts
import * as Sentry from '@sentry/node';

const FLUSH_TIMEOUT_MS = 2000; // 2 seconds before giving up on flush

export function registerShutdownHandlers(
  cleanupFn?: () => Promise<void>,
): void {
  const shutdown = async (signal: string) => {
    console.log(`[Shutdown] ${signal} received — flushing Sentry events`);

    // 1. Flush pending Sentry events with timeout
    try {
      const flushed = await Sentry.close(FLUSH_TIMEOUT_MS);
      console.log(`[Shutdown] Sentry flush: ${flushed ? 'complete' : 'timed out'}`);
    } catch (error) {
      console.error('[Shutdown] Sentry flush error:', error);
    }

    // 2. Run application-specific cleanup
    if (cleanupFn) {
      try {
        await cleanupFn();
      } catch (error) {
        console.error('[Shutdown] Cleanup error:', error);
      }
    }

    process.exit(0);
  };

  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT', () => shutdown('SIGINT'));

  // Last-resort handler — capture, flush, exit
  process.on('uncaughtException', async (error) => {
    console.error('[Fatal] Uncaught exception:', error);
    Sentry.captureException(error);
    try {
      await Sentry.close(FLUSH_TIMEOUT_MS);
    } catch { /* swallow — process is dying anyway */ }
    process.exit(1);
  });

  process.on('unhandledRejection', (reason) => {
    const error = reason instanceof Error ? reason : new Error(String(reason));
    console.error('[Fatal] Unhandled rejection:', error);
    Sentry.captureException(error);
  });
}
```

## Python Graceful Shutdown

```python
import atexit
import sentry_sdk

def _shutdown_flush():
    """atexit handler — flush pending events before interpreter exits."""
    try:
        sentry_sdk.flush(timeout=2)
    except Exception:
        pass

atexit.register(_shutdown_flush)
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io)*
