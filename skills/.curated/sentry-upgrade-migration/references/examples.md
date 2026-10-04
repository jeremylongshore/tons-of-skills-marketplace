# Examples

## Example 1: Express App v7 to v8 Migration

**Request:** "Upgrade our Express API from Sentry v7.114 to v8"

**Before (v7):**

```typescript
// app.ts — everything in one file
import * as Sentry from '@sentry/node';
import { Integrations } from '@sentry/tracing';
import express from 'express';

const app = express();

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  integrations: [
    new Integrations.Express({ app }),
    new Sentry.Integrations.Http({ tracing: true }),
  ],
  tracesSampleRate: 0.2,
});

app.use(Sentry.Handlers.requestHandler());
app.use(Sentry.Handlers.tracingHandler());

app.get('/api/users', async (req, res) => {
  const transaction = Sentry.startTransaction({ name: 'get-users', op: 'http' });
  const span = transaction.startChild({ op: 'db.query', description: 'SELECT users' });

  const users = await db.query('SELECT * FROM users');
  span.finish();
  transaction.finish();

  res.json(users);
});

app.use(Sentry.Handlers.errorHandler());
app.listen(3000);
```

**After (v8):**

```typescript
// instrument.mjs — separate file, loaded first
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 0.2,
  // Express, HTTP, and DB integrations are auto-enabled
});
```

```typescript
// app.mjs — run with: node --import ./instrument.mjs app.mjs
import express from 'express';
import * as Sentry from '@sentry/node';

const app = express();

app.get('/api/users', async (req, res) => {
  // startSpan replaces startTransaction + startChild
  const users = await Sentry.startSpan(
    { name: 'get-users', op: 'http.handler' },
    async () => {
      return Sentry.startSpan(
        { name: 'SELECT users', op: 'db.query' },
        async () => {
          return db.query('SELECT * FROM users');
        }
      );
    }
  );
  res.json(users);
});

// v8: Only error handler remains, with new API
Sentry.setupExpressErrorHandler(app);
app.listen(3000);
```

**Result:** SDK at v8.49.0, `@sentry/tracing` removed, Express auto-instrumented, ESM init pattern applied, source maps re-uploaded.

## Example 2: React App Browser Migration

**Request:** "Migrate our React app's Sentry from v7 to v8"

**Before (v7):**

```typescript
import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';

Sentry.init({
  dsn: '...',
  integrations: [
    new BrowserTracing({
      routingInstrumentation: Sentry.reactRouterV6Instrumentation(
        useEffect, useLocation, useNavigationType, createRoutesFromChildren, matchRoutes
      ),
    }),
    new Sentry.Replay(),
  ],
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});
```

**After (v8):**

```typescript
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: '...',
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration(),
    Sentry.reactRouterV6BrowserTracingIntegration({
      useEffect, useLocation, useNavigationType, createRoutesFromChildren, matchRoutes,
    }),
  ],
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});
```

**Result:** `@sentry/tracing` removed, class-based integrations converted to functions, React Router integration uses new dedicated function.

## Example 3: Python Flask v1 to v2

**Request:** "Upgrade sentry-sdk from 1.40 to 2.x"

**Before (v1):**

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="...",
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.2,
)

# Setting context
with sentry_sdk.configure_scope() as scope:
    scope.set_tag("environment", "production")
    scope.set_user({"id": "user-123"})

# Scoped operations
with sentry_sdk.push_scope() as scope:
    scope.set_extra("request_data", payload)
    sentry_sdk.capture_message("Processing started")
```

**After (v2):**

```python
import sentry_sdk

# Flask integration auto-discovers in v2
sentry_sdk.init(
    dsn="...",
    traces_sample_rate=0.2,
)

# Setting context — direct scope access
scope = sentry_sdk.get_current_scope()
scope.set_tag("environment", "production")
scope.set_user({"id": "user-123"})

# Scoped operations — new_scope replaces push_scope
with sentry_sdk.new_scope() as scope:
    scope.set_extra("request_data", payload)
    sentry_sdk.capture_message("Processing started")
```

**Result:** SDK at 2.x, `configure_scope` replaced, `push_scope` replaced, Flask integration auto-discovered, test error captured.

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
