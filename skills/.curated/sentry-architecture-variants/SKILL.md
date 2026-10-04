---
name: sentry-architecture-variants
description: 'Configure Sentry error tracking and performance monitoring for different

  application architectures. Use when setting up Sentry for monoliths,

  microservices, serverless functions, event-driven systems, frontend SPAs,

  mobile apps, or hybrid deployments.

  Trigger: "sentry monolith setup", "sentry microservices tracing",

  "sentry serverless lambda", "sentry event-driven kafka",

  "sentry react native", "sentry architecture pattern".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(node:*), Bash(npx:*)
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- serverless
- microservices
- architecture
- distributed-tracing
- lambda
- spa
- mobile
compatibility: Designed for Claude Code
---
# Sentry Architecture Variants

## Overview

Choose the right Sentry SDK, project layout, and tracing strategy for each
application architecture. Every pattern below uses Sentry SDK v8 APIs —
`@sentry/node`, `@sentry/browser`, `@sentry/react`, `@sentry/react-native`,
`@sentry/aws-serverless`, and `@sentry/google-cloud-serverless`. The goal is
one coherent trace from the user's device through every backend hop, regardless
of how many runtimes or deployment targets sit in between.

Deep-dive references for each pattern:
[Monolith](references/monolith-architecture.md) |
[Microservices](references/microservices-architecture.md) |
[Serverless](references/serverless-architecture.md) |
[Event-driven](references/event-driven-architecture.md) |
[Frontend SPA](references/frontend-spa-architecture.md) |
[Mobile](references/mobile-architecture.md) |
[Hybrid](references/hybrid-architecture.md) |
[Errors](references/errors.md)

## Prerequisites

- Node.js 18+ (or target platform runtime)
- Sentry organization with at least one project created at [sentry.io](https://sentry.io)
- `SENTRY_DSN` available as an environment variable (one per Sentry project)
- Application architecture documented — service inventory, deployment targets, team ownership mapped
- For distributed tracing: all inter-service transports identified (HTTP, gRPC, Kafka, SQS)

## Instructions

### Step 1 — Identify Your Architecture and Select SDK Packages

Map every runtime in your system to the correct Sentry SDK package and project layout.

| Architecture | SDK Package | Sentry Projects | Key Integration |
|---|---|---|---|
| Monolith | `@sentry/node` | 1 project, env tags | Module tags + ownership rules |
| Microservices | `@sentry/node` (per service) | 1 project per service | Distributed tracing via headers |
| Serverless (Lambda) | `@sentry/aws-serverless` | 1 per function group | `Sentry.wrapHandler()` + auto-flush |
| Serverless (GCP) | `@sentry/google-cloud-serverless` | 1 per function group | `Sentry.wrapCloudEventFunction()` |
| Event-driven (Kafka/SQS) | `@sentry/node` | 1 per consumer group | `continueTrace()` from message headers |
| Frontend SPA | `@sentry/browser` or `@sentry/react` | 1 frontend project | `browserTracingIntegration()` |
| Mobile (React Native) | `@sentry/react-native` | 1 mobile project | Native crash reporting + JS errors |
| Hybrid | Mix of above | 1 per deployment target | Cross-platform trace correlation |

Install the SDK for your architecture:

```bash
# Monolith / Microservices / Event-driven
npm install @sentry/node @sentry/profiling-node

# Serverless — AWS Lambda
npm install @sentry/aws-serverless

# Serverless — Google Cloud Functions
npm install @sentry/google-cloud-serverless

# Frontend SPA (React)
npm install @sentry/react

# Mobile — React Native
npx @sentry/wizard@latest -i reactNative
```

### Step 2 — Initialize Sentry for Each Architecture Pattern

#### Monolith — Single Project, Module Tags

One DSN, one project. Separate concerns with module tags and team ownership rules.

```typescript
// instrument.mjs — load via: node --import ./instrument.mjs app.js
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  release: process.env.APP_VERSION,
  tracesSampleRate: 0.1,
  initialScope: { tags: { app: 'monolith' } },
});

// Tag errors by module so each team sees only their issues
function captureModuleError(module: string, error: Error) {
  Sentry.withScope((scope) => {
    scope.setTag('module', module);
    scope.setTag('team', getTeamForModule(module));
    Sentry.captureException(error);
  });
}

// Module-based breadcrumbs for traceability
Sentry.addBreadcrumb({ category: 'auth', message: 'Login attempt', level: 'info' });
captureModuleError('auth', new Error('Token expired'));
// Dashboard ownership: tags.module:auth → #platform-team
```

#### Microservices — Project-per-Service, Distributed Tracing

Each service gets its own Sentry project. A shared config package keeps init consistent.

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
// Usage: initServiceSentry('api-gateway');
```

HTTP tracing works automatically — SDK v8 propagates `sentry-trace` and `baggage` headers on all outbound HTTP requests. For service mesh (Istio/Linkerd), headers pass through transparently. For non-HTTP transports (gRPC, message queues), see event-driven pattern below and [microservices deep-dive](references/microservices-architecture.md).

#### Serverless — Lambda and Cloud Functions

Serverless SDKs wrap your handler to auto-capture errors and flush events before the runtime freezes.

```typescript
// AWS Lambda — handler.ts
import * as Sentry from '@sentry/aws-serverless';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.STAGE,
  tracesSampleRate: 0.1,
});

export const handler = Sentry.wrapHandler(async (event, context) => {
  Sentry.setTag('function', context.functionName);
  Sentry.setTag('region', process.env.AWS_REGION);

  // Track cold starts
  const isColdStart = !global.__sentryWarm;
  global.__sentryWarm = true;
  Sentry.setTag('cold_start', String(isColdStart));

  const result = await processRequest(event);
  return { statusCode: 200, body: JSON.stringify(result) };
});
// wrapHandler auto-calls flush() — do NOT call it yourself (double-flush causes timeout)
```

```typescript
// Google Cloud Functions — index.ts
import * as Sentry from '@sentry/google-cloud-serverless';

Sentry.init({ dsn: process.env.SENTRY_DSN, tracesSampleRate: 0.1 });

export const httpHandler = Sentry.wrapHttpFunction(async (req, res) => {
  res.json(await processRequest(req.body));
});

export const eventHandler = Sentry.wrapCloudEventFunction(async (event) => {
  await processEvent(event.data);
});
```

#### Event-Driven — Kafka, SQS, and Message Queues

Propagate trace context through message headers so consumer spans connect to producer traces.

```typescript
import * as Sentry from '@sentry/node';

// Producer: embed trace context in message headers
async function publishToKafka(topic: string, payload: object) {
  const activeSpan = Sentry.getActiveSpan();
  const headers: Record<string, string> = {};
  if (activeSpan) {
    headers['sentry-trace'] = Sentry.spanToTraceHeader(activeSpan);
    headers['baggage'] = Sentry.spanToBaggageHeader(activeSpan) || '';
  }
  await Sentry.startSpan(
    { name: `kafka.produce.${topic}`, op: 'queue.publish' },
    () => kafka.send({ topic, messages: [{ value: JSON.stringify(payload), headers }] })
  );
}

// Consumer: continue the producer's trace
async function consumeFromKafka(message: KafkaMessage) {
  const headers = message.headers || {};
  Sentry.continueTrace(
    {
      sentryTrace: headers['sentry-trace']?.toString(), // Buffer → string
      baggage: headers['baggage']?.toString(),
    },
    () => {
      Sentry.startSpan(
        { name: `kafka.consume.${message.topic}`, op: 'queue.process' },
        async (span) => {
          try {
            await processMessage(message);
            span.setStatus({ code: 1 });
          } catch (error) {
            span.setStatus({ code: 2, message: 'consumer_error' });
            Sentry.captureException(error);
            throw error;
          }
        }
      );
    }
  );
}
```

For SQS consumers on Lambda, see [event-driven deep-dive](references/event-driven-architecture.md).

#### Frontend SPA — Browser and React

```typescript
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN,
  release: process.env.REACT_APP_VERSION,
  tracesSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration({ maskAllText: true, blockAllMedia: true }),
  ],
  // Must match your API domain or frontend-to-backend traces break
  tracePropagationTargets: ['localhost', /^https:\/\/api\.yourapp\.com/],
});
```

Route-based transactions, error boundaries, and session replay configuration: see [frontend SPA deep-dive](references/frontend-spa-architecture.md).

#### Mobile — React Native

```typescript
import * as Sentry from '@sentry/react-native';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 0.2,
  integrations: [
    Sentry.reactNativeTracingIntegration({
      routingInstrumentation: Sentry.reactNavigationIntegration(),
    }),
  ],
  tracePropagationTargets: [/^https:\/\/api\.yourapp\.com/],
  enableNativeCrashHandling: true,
  attachScreenshot: true,
  attachViewHierarchy: true,
});

export default Sentry.wrap(App);
// Upload source maps + dSYMs in CI — see mobile deep-dive
```

Full navigation instrumentation and CI upload commands: see [mobile deep-dive](references/mobile-architecture.md).

### Step 3 — Wire Up Hybrid and Cross-Platform Tracing

For systems that span multiple architectures, connect traces end-to-end. The trace flow for a typical hybrid system:

1. `@sentry/react` creates a transaction on user click
2. Browser SDK adds `sentry-trace` + `baggage` headers to `fetch()`
3. API gateway (`@sentry/node`) auto-continues the trace
4. API gateway calls payment-service — headers propagate via HTTP
5. payment-service publishes to Kafka — headers injected manually (see event-driven pattern)
6. Worker (`@sentry/node`) continues trace from Kafka headers

Result: single trace ID visible across all services in Sentry Trace View. Backend-to-frontend correlation requires `tracePropagationTargets` in the browser SDK matching your API domains. Without this, the browser SDK will not attach trace headers and traces break at the browser-to-server boundary. See [hybrid deep-dive](references/hybrid-architecture.md).

**Architecture decision matrix:**

| Architecture | Projects | Tracing Strategy | SDK Flush | Key Gotcha |
|---|---|---|---|---|
| Monolith | 1 | Single-service spans | Automatic | Module tag cardinality — keep under 50 |
| Microservices | 1 per service | Distributed via HTTP headers | Automatic | Missing `baggage` breaks sampling |
| Serverless | 1 per function group | Per-invocation, auto-flush | `wrapHandler()` | Double-flush causes timeout |
| Event-driven | 1 per consumer group | `continueTrace()` from headers | Manual periodic | DLQ needs separate error capture |
| Frontend SPA | 1 | `browserTracingIntegration()` | Automatic (beacon) | `tracePropagationTargets` required |
| Mobile | 1 | `reactNativeTracingIntegration()` | Automatic | Source maps + dSYMs required |
| Hybrid | Mix of above | End-to-end header propagation | Per-component | One missing link breaks whole trace |

## Output

After applying the appropriate pattern, you will have:

- Architecture-specific `Sentry.init()` configuration with correct SDK package
- Distributed tracing connected across all services (HTTP, gRPC, and message queues)
- Serverless handlers wrapped with automatic error capture and event flushing
- Event-driven consumers that continue producer traces via message headers
- Frontend SPA with route-based transactions, session replay, and backend trace correlation
- Mobile app with native crash reporting, screenshot capture, and navigation tracing
- Hybrid systems with end-to-end trace visibility from browser/mobile through every backend hop

## Error Handling

| Error | Cause | Solution |
|---|---|---|
| Distributed traces broken | Missing header propagation | Verify `sentry-trace` AND `baggage` headers in every inter-service call |
| Lambda events lost after timeout | Calling `flush()` inside `wrapHandler` | Remove manual `flush()` — `wrapHandler` auto-flushes |
| Kafka consumer traces disconnected | Headers not serialized as strings | Call `.toString()` on Kafka message headers before `continueTrace()` |
| SPA traces stop at API boundary | `tracePropagationTargets` missing | Add API domain regex to browser SDK init |
| React Native traces unreadable | Missing source maps / dSYMs | Run `sentry-cli sourcemaps upload` and `sentry-cli upload-dif` in CI |
| Multi-tenant data leakage | `setTag()` at global scope | Use `withScope()` per request — global tags persist across requests |
| Worker events silently dropped | No periodic flush | Add `setInterval(() => Sentry.flush(2000), 30_000)` |
| High cardinality alert | Dynamic values in span names | Use parameterized names: `kafka.consume.orders` not `kafka.consume.order-12345` |

See also: [Full error reference](references/errors.md)

## Examples

**Example 1 — Monolith with 5 teams:**
Request: "Set up Sentry for a monolith with auth, billing, inventory, shipping, and analytics modules."
Result: Single Sentry project with `module` and `team` tags. Each team filters issues via `tags.module:billing`. Ownership rules route alerts to the correct Slack channel.

**Example 2 — Microservices with Kafka:**
Request: "Configure Sentry for 12 microservices communicating via REST and Kafka."
Result: 12 Sentry projects with shared `initServiceSentry()`. HTTP traces auto-propagate. Kafka producers inject `sentry-trace`/`baggage` into headers. Consumers call `continueTrace()`. Trace view: `api-gateway -> order-service -> [kafka] -> fulfillment-worker`.

**Example 3 — Serverless API on Lambda:**
Request: "Add Sentry to 8 AWS Lambda functions behind API Gateway."
Result: One Sentry project. Each handler wrapped with `Sentry.wrapHandler()`. Cold starts tagged. No manual `flush()` calls.

**Example 4 — React SPA + Node API:**
Request: "Full-stack Sentry for a React frontend calling a Node.js Express API."
Result: Two projects (frontend + backend). React uses `@sentry/react` with `browserTracingIntegration()` and `replayIntegration()`. `tracePropagationTargets` connects frontend to backend traces.

See also: [Full examples](references/examples.md)

## Resources

- [Node.js SDK Guide](https://docs.sentry.io/platforms/javascript/guides/node/)
- [AWS Lambda Guide](https://docs.sentry.io/platforms/javascript/guides/aws-lambda/)
- [Google Cloud Functions Guide](https://docs.sentry.io/platforms/javascript/guides/gcp-functions/)
- [React SDK Guide](https://docs.sentry.io/platforms/javascript/guides/react/)
- [React Native SDK Guide](https://docs.sentry.io/platforms/react-native/)
- [Distributed Tracing](https://docs.sentry.io/concepts/key-terms/tracing/distributed-tracing/)
- [Session Replay](https://docs.sentry.io/platforms/javascript/session-replay/)
- [Performance Monitoring](https://docs.sentry.io/product/performance/)

## Next Steps

- Run the `sentry-performance-tuning` skill to optimize `tracesSampleRate` and `tracesSampler` for production traffic volumes
- Use `sentry-cost-tuning` to set rate limits and event budgets per project
- Configure `sentry-deploy-integration` to tie releases to deploys for regression detection
- Set up `sentry-multi-env-setup` to manage DSN routing across staging/production
- Apply `sentry-reliability-patterns` for retry logic and circuit breakers around Sentry calls
