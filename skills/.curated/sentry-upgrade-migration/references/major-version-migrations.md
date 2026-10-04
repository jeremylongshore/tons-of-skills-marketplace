# Major Version Migrations

## JavaScript v7 to v8 — Complete Breaking Changes

### 1. Hub Pattern Removed

The Hub concept (`getCurrentHub()`, `configureScope()`, `withScope()` on Hub) is fully removed. All Hub methods are now top-level on the `Sentry` namespace.

```typescript
// v7 (OLD)
const hub = Sentry.getCurrentHub();
const client = hub.getClient();
hub.configureScope((scope) => {
  scope.setTag('key', 'value');
});
hub.captureException(error);
hub.captureMessage('msg');

// v8 (NEW)
const client = Sentry.getClient();
Sentry.withScope((scope) => {
  scope.setTag('key', 'value');
});
Sentry.captureException(error);
Sentry.captureMessage('msg');
```

### 2. Transaction/Span API Replaced with `startSpan()`

`startTransaction()`, `transaction.startChild()`, and manual `.finish()` calls are all removed. Use the callback-based `startSpan()` API which auto-finishes.

```typescript
// v7 (OLD)
const transaction = Sentry.startTransaction({ name: 'process', op: 'task' });
const span = transaction.startChild({ op: 'db.query', description: 'SELECT' });
span.setData('rows', 42);
span.finish();
transaction.setHttpStatus(200);
transaction.finish();

// v8 (NEW)
await Sentry.startSpan({ name: 'process', op: 'task' }, async (rootSpan) => {
  await Sentry.startSpan({ name: 'SELECT', op: 'db.query' }, async (childSpan) => {
    childSpan.setAttribute('rows', 42);
    // auto-finishes when callback returns
  });
  rootSpan.setAttribute('http.status_code', 200);
  // auto-finishes when callback returns
});
```

### 3. Integration Classes Replaced with Functions

All `new Sentry.Integrations.X()` and `new X()` patterns are replaced with `Sentry.xIntegration()` factory functions.

```typescript
// v7 (OLD)
import * as Sentry from '@sentry/node';
import { Integrations } from '@sentry/tracing';

Sentry.init({
  integrations: [
    new Sentry.Integrations.Http({ tracing: true }),
    new Integrations.Express({ app }),
    new Integrations.Mongo(),
  ],
});

// v8 (NEW) — most integrations are auto-enabled
Sentry.init({
  integrations: [
    // Only list integrations you need to configure
    Sentry.httpIntegration({ tracing: true }),
    // Express and Mongo are auto-instrumented via OpenTelemetry
  ],
});
```

### 4. `@sentry/tracing` Package Removed

Tracing functionality is built into `@sentry/node` and `@sentry/browser` in v8.

```bash
# v7
npm install @sentry/node @sentry/tracing

# v8
npm install @sentry/node
npm uninstall @sentry/tracing
```

```typescript
// v7 (OLD)
import { BrowserTracing } from '@sentry/tracing';
Sentry.init({
  integrations: [new BrowserTracing()],
});

// v8 (NEW)
Sentry.init({
  integrations: [Sentry.browserTracingIntegration()],
});
```

### 5. ESM-First Initialization

SDK v8 must be initialized in a separate file loaded before the app to ensure all modules are instrumented.

```typescript
// instrument.mjs
import * as Sentry from '@sentry/node';
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 0.2,
});
```

```bash
# Run with --import flag
node --import ./instrument.mjs app.mjs
```

### 6. Express Handler Changes

```typescript
// v7 (OLD)
app.use(Sentry.Handlers.requestHandler());
app.use(Sentry.Handlers.tracingHandler());
app.use(Sentry.Handlers.errorHandler());

// v8 (NEW) — request and tracing handlers removed (auto-instrumented)
// Only error handler remains, with new API:
Sentry.setupExpressErrorHandler(app);
```

### 7. Transport Interface Change

```typescript
// v7 (OLD) — makeRequest could return void
makeRequest(request: TransportRequest): PromiseLike<TransportMakeRequestResponse | void> {
  sendToBackend(request);
}

// v8 (NEW) — must return TransportMakeRequestResponse
makeRequest(request: TransportRequest): PromiseLike<TransportMakeRequestResponse> {
  sendToBackend(request);
  return Promise.resolve({ statusCode: 200 });
}
```

## JavaScript v6 to v7

### Package Structure Change

```bash
# v6 — single package
npm install @sentry/browser

# v7 — modular packages
npm install @sentry/browser @sentry/tracing
```

### Performance API

```typescript
// v6 — minimal transaction API
Sentry.startTransaction({ name: 'test' });

// v7 — requires op field
const transaction = Sentry.startTransaction({
  name: 'test',
  op: 'task',
});
transaction.finish();
```

## Python SDK v1 to v2

### Scope API Changes

```python
# v1 (OLD)
import sentry_sdk

with sentry_sdk.configure_scope() as scope:
    scope.set_tag("key", "value")

with sentry_sdk.push_scope() as scope:
    scope.set_extra("debug", data)
    sentry_sdk.capture_message("scoped")

# v2 (NEW)
import sentry_sdk

scope = sentry_sdk.get_current_scope()
scope.set_tag("key", "value")

with sentry_sdk.new_scope() as scope:
    scope.set_extra("debug", data)
    sentry_sdk.capture_message("scoped")
```

### Integration Changes

```python
# v1 — some integrations required explicit setup
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="...",
    integrations=[FlaskIntegration()],
)

# v2 — most integrations auto-discovered
# Flask, Django, FastAPI integrations are auto-enabled
# Only list integrations you need to configure
import sentry_sdk
sentry_sdk.init(dsn="...")
```

### Removed APIs

| v1 API | v2 Replacement |
|--------|---------------|
| `configure_scope()` | `get_current_scope()` |
| `push_scope()` | `new_scope()` |
| `Hub.current` | `sentry_sdk.get_current_scope()` |
| `last_event_id()` | `sentry_sdk.last_event_id()` (same) |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
