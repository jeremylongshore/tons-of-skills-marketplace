# Event-Driven Architecture — Sentry Deep Dive

## Kafka — Trace Propagation

### Producer

```typescript
import * as Sentry from '@sentry/node';

async function publishToKafka(topic: string, payload: object) {
  const activeSpan = Sentry.getActiveSpan();
  const headers: Record<string, string> = {};

  if (activeSpan) {
    headers['sentry-trace'] = Sentry.spanToTraceHeader(activeSpan);
    headers['baggage'] = Sentry.spanToBaggageHeader(activeSpan) || '';
  }

  await Sentry.startSpan(
    { name: `kafka.produce.${topic}`, op: 'queue.publish' },
    async () => {
      await kafka.send({
        topic,
        messages: [{ value: JSON.stringify(payload), headers }],
      });
    }
  );
}
```

### Consumer

```typescript
async function consumeFromKafka(message: KafkaMessage) {
  const headers = message.headers || {};

  Sentry.continueTrace(
    {
      sentryTrace: headers['sentry-trace']?.toString(),  // Buffer → string
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

## SQS — Trace Propagation

### Producer (sending to SQS)

```typescript
import { SQSClient, SendMessageCommand } from '@aws-sdk/client-sqs';

async function sendToSQS(queueUrl: string, body: object) {
  const activeSpan = Sentry.getActiveSpan();
  const messageAttributes: Record<string, any> = {};

  if (activeSpan) {
    messageAttributes['sentry-trace'] = {
      DataType: 'String',
      StringValue: Sentry.spanToTraceHeader(activeSpan),
    };
    messageAttributes['baggage'] = {
      DataType: 'String',
      StringValue: Sentry.spanToBaggageHeader(activeSpan) || '',
    };
  }

  await sqs.send(new SendMessageCommand({
    QueueUrl: queueUrl,
    MessageBody: JSON.stringify(body),
    MessageAttributes: messageAttributes,
  }));
}
```

### Consumer (Lambda SQS trigger)

```typescript
import * as Sentry from '@sentry/aws-serverless';

export const handler = Sentry.wrapHandler(async (event) => {
  for (const record of event.Records) {
    const attrs = record.messageAttributes;
    const sentryTrace = attrs?.['sentry-trace']?.stringValue;
    const baggage = attrs?.['baggage']?.stringValue;

    await Sentry.continueTrace({ sentryTrace, baggage }, () => {
      return Sentry.startSpan(
        { name: 'sqs.process', op: 'queue.process' },
        () => processRecord(record)
      );
    });
  }
});
```

## Dead Letter Queue Handling

```typescript
// DLQ consumer should capture the original error context
async function processDLQ(message: DLQMessage) {
  Sentry.withScope((scope) => {
    scope.setTag('queue', 'dlq');
    scope.setTag('original_queue', message.originalQueue);
    scope.setTag('retry_count', String(message.retryCount));
    scope.setContext('original_error', {
      error: message.failureReason,
      timestamp: message.firstFailureAt,
    });

    Sentry.captureMessage(
      `DLQ: ${message.failureReason}`,
      message.retryCount > 5 ? 'error' : 'warning'
    );
  });
}
```

## Long-Running Consumer Flush

For non-serverless consumers (ECS, K8s pods), events buffer in memory. Add periodic flush:

```typescript
// Flush every 30 seconds to prevent event loss on crash
setInterval(() => Sentry.flush(2000), 30_000);

// Also flush on graceful shutdown
process.on('SIGTERM', async () => {
  await Sentry.flush(5000);
  process.exit(0);
});
```

## Common Gotcha: Buffer vs String Headers

Kafka headers are `Buffer` objects, not strings. Always call `.toString()`:

```typescript
// WRONG — headers are Buffers
const sentryTrace = headers['sentry-trace'];

// CORRECT — convert to string
const sentryTrace = headers['sentry-trace']?.toString();
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
