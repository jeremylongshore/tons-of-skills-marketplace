# Examples

## Example 1: Full Express Migration from Rollbar

**Request:** "Migrate our Express API from Rollbar to Sentry"

**Before (Rollbar):**

```typescript
import Rollbar from 'rollbar';
const rollbar = new Rollbar({
  accessToken: process.env.ROLLBAR_TOKEN,
  environment: process.env.NODE_ENV,
});
app.use(rollbar.errorHandler());

// In route handlers:
rollbar.error('Payment failed', { orderId });
rollbar.configure({ person: { id: user.id, email: user.email } });
```

**After (Sentry):**

```typescript
import * as Sentry from '@sentry/node';
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  release: process.env.npm_package_version,
  tracesSampleRate: 0.2,
});
Sentry.setupExpressErrorHandler(app);

// In route handlers:
Sentry.captureException(new Error('Payment failed'));
Sentry.setContext('order', { orderId });
Sentry.setUser({ id: user.id, email: user.email });
```

**Result:** SDK replaced, parallel run for 2 weeks confirmed 98% error count parity, 3 alert rules migrated to Sentry Issue Alerts, Rollbar uninstalled after validation.

## Example 2: React App Migration from Bugsnag

**Request:** "Replace Bugsnag with Sentry in our React SPA"

**Changes:**

1. Replaced `@bugsnag/js` + `@bugsnag/plugin-react` with `@sentry/react`
2. Swapped `Bugsnag.notify()` calls to `Sentry.captureException()`
3. Replaced Bugsnag error boundary with `<Sentry.ErrorBoundary>`
4. Converted `leaveBreadcrumb()` calls to `Sentry.addBreadcrumb()`

**Result:** 47 API call sites updated, error boundary covers 3 route segments, breadcrumb coverage maintained.

## Example 3: New Relic Partial Migration

**Request:** "Move error tracking from New Relic to Sentry, keep APM in New Relic"

**Approach:** New Relic bundles error tracking with APM. Sentry replaces only the error tracking portion. Keep `newrelic` agent running for APM (response times, throughput, infrastructure). Add Sentry alongside for dedicated error tracking with better grouping and stack traces.

```typescript
// Keep New Relic for APM
import 'newrelic';  // must be first import

// Add Sentry for error tracking
import * as Sentry from '@sentry/node';
Sentry.init({ dsn: process.env.SENTRY_DSN });

// Stop calling newrelic.noticeError() -- Sentry handles errors now
// Keep newrelic.recordCustomEvent() for APM custom metrics
```

**Result:** Error tracking moved to Sentry, APM stays in New Relic, total cost reduced by removing New Relic error tracking license seats.

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
