# Buffering And Batching

## Buffering and Batching

### Client-Side Buffering

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Buffer events before sending
  transport: Sentry.makeNodeTransport,
  transportOptions: {
    // Increase buffer size for high volume
    bufferSize: 1000,
  },
});
```

### Custom Batching Transport

```typescript
class BatchingTransport {
  private buffer: Sentry.Event[] = [];
  private flushInterval: NodeJS.Timer;

  constructor(private batchSize = 100, private flushMs = 5000) {
    this.flushInterval = setInterval(() => this.flush(), flushMs);
  }

  send(event: Sentry.Event) {
    this.buffer.push(event);
    if (this.buffer.length >= this.batchSize) {
      this.flush();
    }
  }

  private async flush() {
    if (this.buffer.length === 0) return;

    const batch = this.buffer.splice(0, this.batchSize);
    // Send batch to Sentry
    await this.sendBatch(batch);
  }

  private async sendBatch(events: Sentry.Event[]) {
    // Use envelope format for batch sending
    for (const event of events) {
      await Sentry.captureEvent(event);
    }
  }
}
```
