## Examples

### Full Test Script (TypeScript)

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({ dsn: process.env.SENTRY_DSN });

// Set user context
Sentry.setUser({ id: '123', email: 'test@example.com' });

// Set tags
Sentry.setTag('environment', 'test');
Sentry.setTag('version', '1.0.0');

// Capture different event types
Sentry.captureMessage('Info message', 'info');
Sentry.captureMessage('Warning message', 'warning');

try {
  throw new Error('Test exception');
} catch (e) {
  Sentry.captureException(e);
}

console.log('Events sent - check Sentry dashboard');
```

### Python Test Script

```python
import sentry_sdk

sentry_sdk.init(dsn=os.environ.get('SENTRY_DSN'))

sentry_sdk.set_user({'id': '123', 'email': 'test@example.com'})
sentry_sdk.set_tag('environment', 'test')

sentry_sdk.capture_message('Hello from Python!')

try:
    raise ValueError('Test exception from Python')
except Exception as e:
    sentry_sdk.capture_exception(e)
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
