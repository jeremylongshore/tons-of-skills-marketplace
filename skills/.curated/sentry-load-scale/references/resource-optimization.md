# Resource Optimization

## Resource Optimization

### Minimal SDK Configuration

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Reduce memory usage
  maxBreadcrumbs: 10, // Default is 100
  maxValueLength: 250, // Truncate long strings

  // Disable unused features
  autoSessionTracking: false,
  sendDefaultPii: false,

  // Minimal integrations
  integrations: (defaults) =>
    defaults.filter((i) =>
      ['Http', 'OnUncaughtException', 'OnUnhandledRejection'].includes(i.name)
    ),
});
```

### Async Event Processing

```typescript
// Don't block request handling
async function handleRequest(req: Request, res: Response) {
  try {
    const result = await processRequest(req);
    res.json(result);
  } catch (error) {
    // Capture async - don't await
    setImmediate(() => Sentry.captureException(error));

    res.status(500).json({ error: 'Internal error' });
  }
}
```

### Background Flushing

```typescript
// Flush on graceful shutdown
process.on('SIGTERM', async () => {
  console.log('Flushing Sentry events...');
  await Sentry.close(10000); // 10 second timeout
  process.exit(0);
});

// Periodic flush for long-running processes
setInterval(() => {
  Sentry.flush(5000);
}, 60000); // Every minute
```
