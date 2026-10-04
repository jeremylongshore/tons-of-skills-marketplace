## Implementation Guide

### Step 1: Capture Test Error

```typescript
import * as Sentry from '@sentry/node';

try {
  throw new Error('Hello Sentry! This is a test error.');
} catch (error) {
  Sentry.captureException(error);
  console.log('Error sent to Sentry');
}
```

### Step 2: Capture Test Message

```typescript
Sentry.captureMessage('Hello from Sentry SDK!', 'info');
```

### Step 3: Verify in Dashboard

1. Open https://sentry.io
2. Navigate to your project
3. Check Issues tab for the test error
4. Verify event details are correct

### Step 4: Add Context

```typescript
Sentry.setUser({ id: 'test-user', email: 'test@example.com' });
Sentry.setTag('test_run', 'hello-world');
Sentry.captureMessage('Test with context');
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
