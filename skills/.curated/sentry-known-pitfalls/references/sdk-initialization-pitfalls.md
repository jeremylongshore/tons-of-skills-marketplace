# SDK Initialization Pitfalls

## Pitfall 3: Not Calling `flush()` in Serverless or CLI

Sentry queues events in memory and sends asynchronously. In serverless functions and CLI scripts, the process exits before the queue drains. Events are captured but never sent.

```typescript
// WRONG — Lambda exits before events send
export const handler = async (event) => {
  try {
    return await processEvent(event);
  } catch (error) {
    Sentry.captureException(error);
    throw error;  // Events still in queue, never sent
  }
};

// RIGHT — flush before returning
export const handler = async (event) => {
  try {
    return await processEvent(event);
  } catch (error) {
    Sentry.captureException(error);
    await Sentry.flush(2000);
    throw error;
  }
};

// BEST — use framework wrapper
import * as Sentry from '@sentry/aws-serverless';
export const handler = Sentry.wrapHandler(async (event) => {
  return await processEvent(event);
});
```

## Pitfall 8: Importing `@sentry/node` in Browser Bundle

`@sentry/node` depends on Node.js built-ins (`http`, `fs`, `path`). Importing it in browser code causes build failures, 100KB+ polyfill bloat, or runtime crashes.

```typescript
// WRONG — Node SDK in React
import * as Sentry from '@sentry/node';

// RIGHT — platform-specific SDK
import * as Sentry from '@sentry/react';    // React
import * as Sentry from '@sentry/vue';      // Vue
import * as Sentry from '@sentry/nextjs';   // Next.js (handles both)
import * as Sentry from '@sentry/node';     // Server-only code
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
