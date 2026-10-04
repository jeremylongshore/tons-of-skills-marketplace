---
name: sentry-sdk-patterns
description: 'Best practices for using Sentry SDK in TypeScript and Python.

  Use when implementing structured error context with scopes, breadcrumb

  strategies, beforeSend/beforeBreadcrumb filtering, custom fingerprinting,

  user context, or performance span creation.

  Trigger: "sentry best practices", "sentry patterns", "sentry sdk usage",

  "sentry scope", "sentry breadcrumbs", "sentry beforeSend", "sentry fingerprint".

  '
allowed-tools: Read, Write, Edit, Grep
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- python
- typescript
- best-practices
- error-handling
compatibility: Designed for Claude Code
---
# Sentry SDK Patterns

## Overview

Production patterns for `@sentry/node` (v8+) and `sentry-sdk` (Python 2.x+) covering scoped error context, breadcrumb strategies, event filtering with `beforeSend`, custom fingerprinting for issue grouping, and performance instrumentation with spans. All examples use real Sentry SDK APIs.

## Prerequisites

- Sentry SDK v8+ installed (`@sentry/node`, `@sentry/react`, or `sentry-sdk`)
- `SENTRY_DSN` environment variable configured
- Familiarity with async/await (TypeScript) or context managers (Python)

## Instructions

### Step 1 -- Structured Error Context with Scopes

Use `Sentry.withScope()` (TypeScript) or `sentry_sdk.new_scope()` (Python) to attach context to individual events without leaking state across requests.

**TypeScript -- Scoped error capture:**

```typescript
import * as Sentry from '@sentry/node';

type ErrorSeverity = 'low' | 'medium' | 'high' | 'critical';

interface ErrorOptions {
  severity?: ErrorSeverity;
  tags?: Record<string, string>;
  context?: Record<string, unknown>;
  user?: { id: string; email?: string };
  fingerprint?: string[];
}

const SEVERITY_MAP: Record<ErrorSeverity, Sentry.SeverityLevel> = {
  low: 'info',
  medium: 'warning',
  high: 'error',
  critical: 'fatal',
};

export function captureError(error: Error, options: ErrorOptions = {}) {
  Sentry.withScope((scope) => {
    scope.setLevel(SEVERITY_MAP[options.severity || 'medium']);

    if (options.tags) {
      Object.entries(options.tags).forEach(([key, value]) => {
        scope.setTag(key, value);
      });
    }
    if (options.context) {
      scope.setContext('app', options.context);
    }
    if (options.user) {
      scope.setUser(options.user);
    }
    if (options.fingerprint) {
      scope.setFingerprint(options.fingerprint);
    }

    Sentry.captureException(error);
  });
}
```

**Python -- Scoped error capture:**

```python
import sentry_sdk

def capture_error(error, severity="error", tags=None, context=None, user=None):
    """Capture exception with isolated scope context."""
    with sentry_sdk.new_scope() as scope:
        scope.set_level(severity)
        if tags:
            for key, value in tags.items():
                scope.set_tag(key, value)
        if context:
            scope.set_context("app", context)
        if user:
            scope.set_user(user)
        sentry_sdk.capture_exception(error)
```

**Key rule:** Never call `Sentry.setTag()` or `sentry_sdk.set_tag()` at the module level inside request handlers. Those mutate the global scope and leak between concurrent requests. Always use `withScope()` or `new_scope()`.

### Step 2 -- Breadcrumbs, Filtering, and Fingerprints

#### Structured breadcrumb helpers

```typescript
import * as Sentry from '@sentry/node';

export const breadcrumb = {
  auth(action: string, userId?: string) {
    Sentry.addBreadcrumb({
      category: 'auth',
      message: `${action}${userId ? ` for user ${userId}` : ''}`,
      level: 'info',
    });
  },

  db(operation: string, table: string, durationMs?: number) {
    Sentry.addBreadcrumb({
      category: 'db',
      message: `${operation} on ${table}`,
      level: 'info',
      data: { table, operation, ...(durationMs && { duration_ms: durationMs }) },
    });
  },

  http(method: string, url: string, status: number) {
    Sentry.addBreadcrumb({
      category: 'http',
      message: `${method} ${url} -> ${status}`,
      level: status >= 400 ? 'warning' : 'info',
      data: { method, url, status_code: status },
    });
  },
};
```

**Python breadcrumbs:**

```python
sentry_sdk.add_breadcrumb(
    category="auth", message="User logged in",
    level="info", data={"user_id": user_id, "method": "oauth"},
)
```

#### beforeSend -- Drop noise, scrub PII

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  beforeSend(event, hint) {
    const error = hint?.originalException;
    // Drop non-actionable errors
    if (error instanceof Error) {
      if (error.message.includes('ResizeObserver loop')) return null;
      if (error.message.includes('Network request failed')) return null;
    }
    // Scrub PII from user context
    if (event.user) {
      delete event.user.ip_address;
      delete event.user.email;
    }
    return event;
  },
});
```

**Python beforeSend:**

```python
def before_send(event, hint):
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]
        if isinstance(exc_value, (KeyboardInterrupt, SystemExit)):
            return None
    if "user" in event:
        event["user"].pop("email", None)
        event["user"].pop("ip_address", None)
    return event

sentry_sdk.init(dsn=os.environ["SENTRY_DSN"], before_send=before_send)
```

#### beforeBreadcrumb -- Filter noisy breadcrumbs

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  beforeBreadcrumb(breadcrumb, hint) {
    // Drop console.log breadcrumbs in production
    if (breadcrumb.category === 'console' && breadcrumb.level === 'log') {
      return null;
    }
    // Redact auth tokens from HTTP breadcrumbs
    if (breadcrumb.category === 'fetch' && breadcrumb.data?.url) {
      const url = new URL(breadcrumb.data.url);
      url.searchParams.delete('token');
      breadcrumb.data.url = url.toString();
    }
    return breadcrumb;
  },
});
```

#### Custom fingerprints for issue grouping

Override default stack-trace grouping when the same root cause produces different stacks:

```typescript
Sentry.withScope((scope) => {
  // Group all payment gateway timeouts together
  scope.setFingerprint(['payment-gateway-timeout', gatewayName]);
  Sentry.captureException(error);
});
```

```python
with sentry_sdk.new_scope() as scope:
    scope.fingerprint = ["payment-gateway-timeout", gateway_name]
    sentry_sdk.capture_exception(error)
```

### Step 3 -- Framework Integration and Performance Spans

#### Express middleware (Sentry v8)

```typescript
import * as Sentry from '@sentry/node';
import express from 'express';

const app = express();

// Sentry v8: register error handler
Sentry.setupExpressErrorHandler(app);

// Request context middleware (register BEFORE routes)
app.use((req, res, next) => {
  Sentry.setUser({ id: req.user?.id, ip_address: req.ip });
  Sentry.addBreadcrumb({
    category: 'http',
    message: `${req.method} ${req.path}`,
    data: { query: req.query, params: req.params },
  });
  next();
});
```

#### React Error Boundary

```tsx
import * as Sentry from '@sentry/react';

const SentryErrorBoundary = Sentry.withErrorBoundary(App, {
  fallback: ({ error, resetError }) => (
    <div>
      <h2>Something went wrong</h2>
      <button onClick={resetError}>Try again</button>
    </div>
  ),
  beforeCapture: (scope) => {
    scope.setTag('location', 'error-boundary');
    scope.setLevel('fatal');
  },
});
```

#### Performance spans (TypeScript)

```typescript
async function processOrder(orderId: string) {
  return Sentry.startSpan(
    { name: 'processOrder', op: 'task', attributes: { orderId } },
    async (span) => {
      const order = await Sentry.startSpan(
        { name: 'db.getOrder', op: 'db.query' },
        () => db.orders.findById(orderId),
      );
      await Sentry.startSpan(
        { name: 'payment.charge', op: 'http.client' },
        () => chargePayment(order),
      );
      span.setStatus({ code: 1, message: 'ok' });
      return order;
    },
  );
}
```

#### Performance spans (Python)

```python
import sentry_sdk
from functools import wraps

def sentry_traced(op="function"):
    """Decorator to wrap functions in Sentry spans."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with sentry_sdk.start_span(op=op, name=func.__name__):
                return func(*args, **kwargs)
        return wrapper
    return decorator

@sentry_traced(op="db.query")
def get_user(user_id: str):
    return db.users.find_one({"_id": user_id})
```

#### Async batch processing with error isolation

```typescript
async function processItems(items: Item[]) {
  const results = await Promise.allSettled(
    items.map((item) =>
      Sentry.startSpan({ name: `process.${item.type}`, op: 'task' }, () =>
        processItem(item),
      ),
    ),
  );

  const failures = results.filter(
    (r): r is PromiseRejectedResult => r.status === 'rejected',
  );

  if (failures.length > 0) {
    Sentry.withScope((scope) => {
      scope.setTag('batch_size', String(items.length));
      scope.setTag('failure_count', String(failures.length));
      Sentry.captureMessage(`${failures.length}/${items.length} items failed`, 'warning');
    });
    failures.forEach((f) => Sentry.captureException(f.reason));
  }
}
```

See [implementation.md](references/implementation.md) for Django middleware, test mocking patterns, and additional framework examples.

## Output

After applying these patterns you will have:

- Centralized error handler module with typed severity and scoped context
- Structured breadcrumb helpers for auth, db, and http events
- `beforeSend` filter that drops noise and scrubs PII
- `beforeBreadcrumb` callback that redacts sensitive query parameters
- Custom fingerprinting for accurate issue grouping
- Framework error boundaries for Express and React
- Performance spans for tracing critical code paths

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Scope leaking between requests | Global scope mutations in async handlers | Use `withScope()` / `new_scope()` for per-event context |
| Duplicate events | Error caught and re-thrown at two layers | Capture at one level only -- middleware or handler, not both |
| Missing breadcrumbs | Cleared after max count (default 100) | Set `maxBreadcrumbs` in `Sentry.init()` |
| `beforeSend` returns `undefined` | Missing return statement | Always return `event` or `null` explicitly |
| Events grouped incorrectly | Default stack-trace fingerprinting | Use `scope.setFingerprint()` with semantic keys |
| `Sentry is not defined` | SDK not imported | Verify `import * as Sentry from '@sentry/node'` |
| Spans not appearing | Missing tracing config | Set `tracesSampleRate` in `Sentry.init()` |

## Examples

**Centralized error handler:** Create `lib/error-handler.ts` wrapping `Sentry.withScope()` with typed severity, tags, context, user, and fingerprint support.

**Breadcrumb trail for checkout:** Add `breadcrumb.auth('login')`, `breadcrumb.db('SELECT', 'orders')`, `breadcrumb.http('POST', '/api/payments', 201)` before critical operations so errors include full context timeline.

**Noise filtering:** Configure `beforeSend` to drop `ResizeObserver loop` and `Network request failed`, scrub PII from user context and cookies.

**Fix issue grouping:** Add `scope.setFingerprint(['payment-gateway-timeout', gatewayName])` to group all payment timeouts by gateway.

See [examples.md](references/examples.md) for full worked scenarios with Python context managers and async wrappers.

## Resources

- [Sentry JavaScript SDK Best Practices](https://docs.sentry.io/platforms/javascript/best-practices/)
- [Scopes and Context](https://docs.sentry.io/platforms/javascript/enriching-events/scopes/)
- [Express Integration Guide](https://docs.sentry.io/platforms/javascript/guides/express/)
- [Python SDK Documentation](https://docs.sentry.io/platforms/python/)
- [Custom Fingerprinting](https://docs.sentry.io/platforms/javascript/enriching-events/fingerprinting/)
- [Performance Monitoring](https://docs.sentry.io/platforms/javascript/tracing/)

## Next Steps

- **sentry-error-capture** -- Deep dive on `captureException` vs `captureMessage` semantics
- **sentry-performance-tracing** -- Full distributed tracing with `tracesSampleRate` and custom instrumentation
- **sentry-data-handling** -- PII scrubbing, data residency, and GDPR-compliant configuration
- **sentry-common-errors** -- Troubleshooting guide for frequent SDK issues
