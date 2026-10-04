# Serverless Architecture — Sentry Deep Dive

## AWS Lambda

```typescript
import * as Sentry from '@sentry/aws-serverless';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.STAGE,
  tracesSampleRate: 0.1,
});

export const handler = Sentry.wrapHandler(async (event, context) => {
  Sentry.setTag('function', context.functionName);
  Sentry.setTag('region', process.env.AWS_REGION);

  // Cold start tracking
  const isColdStart = !global.__sentryWarm;
  global.__sentryWarm = true;
  Sentry.setTag('cold_start', String(isColdStart));

  const result = await processRequest(event);
  return { statusCode: 200, body: JSON.stringify(result) };
});
// wrapHandler auto-calls Sentry.flush() — do NOT call it yourself
```

## Google Cloud Functions

```typescript
import * as Sentry from '@sentry/google-cloud-serverless';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 0.1,
});

// HTTP function
export const httpHandler = Sentry.wrapHttpFunction(async (req, res) => {
  const result = await processRequest(req.body);
  res.json(result);
});

// CloudEvent function (Pub/Sub, Firestore triggers)
export const eventHandler = Sentry.wrapCloudEventFunction(async (event) => {
  await processEvent(event.data);
});
```

## Critical: Flush Behavior

| Platform | Wrapper | Auto-flush? | Manual flush needed? |
|---|---|---|---|
| AWS Lambda | `Sentry.wrapHandler()` | Yes | No — double-flush causes timeout |
| GCP Functions | `Sentry.wrapHttpFunction()` | Yes | No |
| GCP CloudEvent | `Sentry.wrapCloudEventFunction()` | Yes | No |
| Vercel | `@sentry/nextjs` | Yes | No |

**Never call `Sentry.flush()` inside a wrapped serverless handler.** The wrapper already handles it. Calling it manually causes the function to wait for two flush cycles, often exceeding the timeout.

## Cold Start Spans

```typescript
// Track cold start duration as a span
if (!global.__sentryWarm) {
  global.__sentryWarm = true;
  Sentry.startSpan({ name: 'lambda.cold_start', op: 'function' }, () => {
    // initialization code measured here
    initializeConnections();
    loadConfiguration();
  });
}
```

## SQS Trigger with Trace Continuation

```typescript
export const handler = Sentry.wrapHandler(async (event) => {
  for (const record of event.Records) {
    const attrs = record.messageAttributes;
    const sentryTrace = attrs?.['sentry-trace']?.stringValue;
    const baggage = attrs?.['baggage']?.stringValue;

    await Sentry.continueTrace({ sentryTrace, baggage }, () => {
      return Sentry.startSpan(
        { name: `sqs.process`, op: 'queue.process' },
        () => processRecord(record)
      );
    });
  }
});
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
