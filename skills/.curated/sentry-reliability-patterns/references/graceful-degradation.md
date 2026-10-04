# Graceful Degradation

## Safe Initialization — TypeScript

```typescript
// lib/sentry-safe.ts — never let Sentry crash your app
import * as Sentry from '@sentry/node';

let sentryAvailable = false;

export function initSentrySafe(
  dsn: string,
  options: Partial<Sentry.NodeOptions> = {},
): boolean {
  try {
    Sentry.init({
      dsn,
      environment: options.environment ?? process.env.NODE_ENV ?? 'development',
      release: options.release ?? process.env.RELEASE_SHA,
      sampleRate: options.sampleRate ?? 1.0,
      ...options,
      beforeSend(event, hint) {
        // Wrap user-supplied beforeSend — don't let it crash the pipeline
        try {
          return options.beforeSend?.(event, hint) ?? event;
        } catch (hookError) {
          console.error('[Sentry] beforeSend hook threw:', hookError);
          return event; // Send event even if hook fails
        }
      },
    });

    // Verify client was actually created (invalid DSN silently produces no client)
    sentryAvailable = !!Sentry.getClient();
    if (!sentryAvailable) {
      console.warn('[Sentry] Client not created — DSN may be invalid or empty');
    }
    return sentryAvailable;
  } catch (error) {
    console.error('[Sentry] Initialization failed, app continues without Sentry:', error);
    sentryAvailable = false;
    return false;
  }
}

/** Check if Sentry is operational before calling capture methods. */
export function isSentryActive(): boolean {
  return sentryAvailable;
}

/** Mark Sentry as unavailable (called by circuit breaker when tripped). */
export function setSentryUnavailable(): void {
  sentryAvailable = false;
}

/** Capture an error with automatic fallback to local logging. */
export function captureError(
  error: Error,
  context?: Record<string, unknown>,
): string | undefined {
  // Always log locally as baseline — never lose the error entirely
  console.error(`[Error] ${error.name}: ${error.message}`, context ?? '');

  if (!sentryAvailable) {
    writeToFallbackLog(error, context);
    return undefined;
  }

  try {
    let eventId: string | undefined;
    Sentry.withScope((scope) => {
      if (context) scope.setContext('error_context', context);
      eventId = Sentry.captureException(error);
    });
    return eventId;
  } catch (sentryError) {
    console.error('[Sentry] captureException failed:', sentryError);
    writeToFallbackLog(error, context);
    return undefined;
  }
}

function writeToFallbackLog(error: Error, context?: Record<string, unknown>): void {
  const entry = {
    timestamp: new Date().toISOString(),
    error: { name: error.name, message: error.message, stack: error.stack },
    context,
  };
  // Replace with structured file logger or external service in production
  console.error('[Fallback Log]', JSON.stringify(entry));
}
```

## Application Entrypoint Wiring

```typescript
// app.ts — startup
import { initSentrySafe } from './lib/sentry-safe';

const sentryReady = initSentrySafe(process.env.SENTRY_DSN ?? '', {
  environment: process.env.NODE_ENV,
  release: process.env.RELEASE_SHA,
  tracesSampleRate: 0.2,
});

console.log(`Sentry status: ${sentryReady ? 'active' : 'degraded (fallback logging)'}`);

// App starts regardless of Sentry status
startServer();
```

## Safe Initialization — Python

```python
import sentry_sdk
import os

_sentry_available = False

def init_sentry_safe(dsn: str, **kwargs) -> bool:
    """Initialize Sentry safely — app continues if SDK fails."""
    global _sentry_available
    try:
        sentry_sdk.init(
            dsn=dsn,
            environment=kwargs.get("environment", os.getenv("SENTRY_ENVIRONMENT", "development")),
            release=kwargs.get("release", os.getenv("RELEASE_SHA")),
            traces_sample_rate=kwargs.get("traces_sample_rate", 0.2),
            **{k: v for k, v in kwargs.items()
               if k not in ("environment", "release", "traces_sample_rate")},
        )
        client = sentry_sdk.get_client()
        _sentry_available = client is not None and client.is_active()
        if not _sentry_available:
            print("[Sentry] Client not active — DSN may be invalid")
        return _sentry_available
    except Exception as e:
        print(f"[Sentry] Init failed, app continues without Sentry: {e}")
        _sentry_available = False
        return False

def is_sentry_active() -> bool:
    return _sentry_available
```

## Missing DSN Handling

```typescript
Sentry.init({
  // DSN can be undefined — SDK disables itself gracefully
  dsn: process.env.SENTRY_DSN,
  enabled: !!process.env.SENTRY_DSN,
  beforeSend(event) {
    // Only called if DSN is set
    return event;
  },
});

// Safe to call even without DSN — becomes a no-op
Sentry.captureMessage('Test');
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io)*
