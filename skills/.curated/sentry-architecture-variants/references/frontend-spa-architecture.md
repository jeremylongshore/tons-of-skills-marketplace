# Frontend SPA Architecture — Sentry Deep Dive

## React Setup with @sentry/react

```typescript
// src/instrument.ts — load before app mounts
import * as Sentry from '@sentry/react';
import { createBrowserRouter } from 'react-router-dom';

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  release: process.env.REACT_APP_VERSION,
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1,         // 10% of sessions recorded
  replaysOnErrorSampleRate: 1.0,         // 100% of error sessions recorded

  integrations: [
    Sentry.browserTracingIntegration(),  // auto-instruments page loads + XHR
    Sentry.replayIntegration({
      maskAllText: true,                 // PII-safe by default
      blockAllMedia: true,
    }),
  ],

  // Connect frontend spans to backend traces
  tracePropagationTargets: [
    'localhost',
    /^https:\/\/api\.yourapp\.com/,      // your API domain
  ],
});

// Route-based transactions with React Router v6+
const sentryCreateBrowserRouter = Sentry.wrapCreateBrowserRouterV6(createBrowserRouter);

const router = sentryCreateBrowserRouter([
  { path: '/', element: <Home /> },
  { path: '/dashboard', element: <Dashboard /> },
  { path: '/settings', element: <Settings /> },
]);

// Error boundary captures React component errors
function App() {
  return (
    <Sentry.ErrorBoundary
      fallback={({ error }) => <ErrorPage error={error} />}
      showDialog                          // shows user feedback dialog
    >
      <RouterProvider router={router} />
    </Sentry.ErrorBoundary>
  );
}
```

## Vanilla JS / Vue / Angular

Use `@sentry/browser` instead of `@sentry/react`:

```typescript
import * as Sentry from '@sentry/browser';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  integrations: [Sentry.browserTracingIntegration()],
  tracesSampleRate: 0.1,
  tracePropagationTargets: ['localhost', /^https:\/\/api\.yourapp\.com/],
});
```

## Critical: tracePropagationTargets

The browser SDK will NOT attach `sentry-trace`/`baggage` headers to API requests unless the URL matches `tracePropagationTargets`. Without this, frontend-to-backend traces break.

```typescript
// WRONG — no targets, no headers sent
Sentry.init({ dsn: '...' });

// CORRECT — headers sent to matching API domains
Sentry.init({
  dsn: '...',
  tracePropagationTargets: [
    'localhost',
    /^https:\/\/api\.yourapp\.com/,
  ],
});
```

## Session Replay Configuration

Session Replay records DOM changes (not video) for error reproduction:

```typescript
Sentry.init({
  integrations: [
    Sentry.replayIntegration({
      maskAllText: true,       // mask all text for PII safety
      blockAllMedia: true,     // block images/video
      maskAllInputs: true,     // mask form inputs
    }),
  ],
  replaysSessionSampleRate: 0.1,   // 10% of all sessions
  replaysOnErrorSampleRate: 1.0,   // 100% of sessions with errors
});
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
