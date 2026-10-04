# Microservices Architecture — Sentry Deep Dive

## Project Layout

```
Organization: mycompany
├── Project: api-gateway        (DSN_GATEWAY)
├── Project: user-service       (DSN_USERS)
├── Project: payment-service    (DSN_PAYMENTS)
├── Project: notification-svc   (DSN_NOTIFICATIONS)
└── Project: frontend-web       (DSN_FRONTEND)
```

Each service gets its own project and DSN for isolated error budgets and team ownership.

## Shared Configuration Package

```typescript
// packages/sentry-config/index.ts — shared across all services
import * as Sentry from '@sentry/node';

export function initServiceSentry(serviceName: string) {
  Sentry.init({
    dsn: process.env.SENTRY_DSN,
    environment: process.env.NODE_ENV,
    release: `${serviceName}@${process.env.APP_VERSION}`,
    serverName: serviceName,
    tracesSampleRate: 0.1,
    sendDefaultPii: false,

    initialScope: {
      tags: {
        service: serviceName,
        cluster: process.env.K8S_CLUSTER || 'default',
        namespace: process.env.K8S_NAMESPACE || 'default',
      },
    },
  });
}

// Usage in each service's instrument.mjs:
// import { initServiceSentry } from '@mycompany/sentry-config';
// initServiceSentry('user-service');
```

## Distributed Tracing — HTTP

SDK v8 auto-propagates `sentry-trace` and `baggage` headers on all HTTP requests. No manual work needed for `fetch()`, `axios`, or `http.request()`.

Service mesh proxies (Istio, Linkerd) pass these headers transparently.

## Distributed Tracing — gRPC

```typescript
// gRPC client — inject headers into metadata
function callGrpcService(client: GrpcClient, method: string, request: any) {
  const metadata = new grpc.Metadata();
  const span = Sentry.getActiveSpan();

  if (span) {
    metadata.set('sentry-trace', Sentry.spanToTraceHeader(span));
    metadata.set('baggage', Sentry.spanToBaggageHeader(span) || '');
  }

  return Sentry.startSpan(
    { name: `grpc.${method}`, op: 'grpc.client' },
    () => clientmethod
  );
}

// gRPC server — continue trace from incoming metadata
function handleGrpcRequest(call: ServerUnaryCall, callback: sendUnaryData) {
  const sentryTrace = call.metadata.get('sentry-trace')[0]?.toString();
  const baggage = call.metadata.get('baggage')[0]?.toString();

  Sentry.continueTrace({ sentryTrace, baggage }, () => {
    Sentry.startSpan(
      { name: `grpc.${call.getPath()}`, op: 'grpc.server' },
      () => processRequest(call, callback)
    );
  });
}
```

## Cross-Service Trace View

In the Sentry Trace View, a distributed trace shows as a waterfall:

```
api-gateway: POST /api/orders         [200ms]
├── user-service: GET /users/123      [ 45ms]
├── payment-service: POST /charge     [120ms]
│   └── stripe-api: POST /charges     [ 80ms]
└── notification-svc: POST /email     [ 15ms]
```

All spans share a single `trace_id`, linked by `sentry-trace` headers.

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
