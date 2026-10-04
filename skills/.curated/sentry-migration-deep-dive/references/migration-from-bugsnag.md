# Migration From Bugsnag

## Concept Mapping: Bugsnag to Sentry

Bugsnag "errors" correspond to Sentry "issues." Bugsnag "events" correspond to Sentry "events." Bugsnag's `releaseStage` maps to Sentry's `environment`. Bugsnag's `appVersion` maps to Sentry's `release`.

### SDK Replacement (Node.js)

```typescript
// BEFORE: Bugsnag initialization
import Bugsnag from '@bugsnag/node';
Bugsnag.start({
  apiKey: process.env.BUGSNAG_KEY,
  releaseStage: process.env.NODE_ENV,
  appVersion: process.env.npm_package_version,
  enabledReleaseStages: ['production', 'staging'],
});

// AFTER: Sentry initialization
import * as Sentry from '@sentry/node';
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  release: process.env.npm_package_version,
  tracesSampleRate: 0.1,
});
```

### API Call Translation Table

| Bugsnag | Sentry | Notes |
|---------|--------|-------|
| `Bugsnag.notify(err)` | `Sentry.captureException(err)` | Direct replacement |
| `Bugsnag.notify(err, onError)` | `Sentry.withScope(scope => { ... })` | Use scope for metadata |
| `Bugsnag.leaveBreadcrumb(msg)` | `Sentry.addBreadcrumb({ message: msg })` | Add `category` and `level` |
| `Bugsnag.setUser(id, email, name)` | `Sentry.setUser({ id, email, username: name })` | Note: `name` becomes `username` |
| `bugsnag.addMetadata(tab, data)` | `Sentry.setContext(tab, data)` | Tab name becomes context key |
| `onError` callback | `beforeSend` hook in `Sentry.init()` | Return null to drop event |
| `enabledReleaseStages` | Custom `beforeSend` filter | Filter by `event.environment` |
| `@bugsnag/plugin-express` | `Sentry.setupExpressErrorHandler(app)` | Built into `@sentry/node` v8+ |

### React Integration Migration

```tsx
// BEFORE: Bugsnag React error boundary
import Bugsnag from '@bugsnag/js';
import BugsnagPluginReact from '@bugsnag/plugin-react';
Bugsnag.start({
  apiKey: process.env.BUGSNAG_KEY,
  plugins: [new BugsnagPluginReact()],
});
const ErrorBoundary = Bugsnag.getPlugin('react')!.createErrorBoundary(React);

<ErrorBoundary>
  <App />
</ErrorBoundary>

// AFTER: Sentry React error boundary
import * as Sentry from '@sentry/react';
Sentry.init({ dsn: process.env.SENTRY_DSN });

<Sentry.ErrorBoundary fallback={<p>Something went wrong</p>}>
  <App />
</Sentry.ErrorBoundary>
```

### Metadata Migration Pattern

```typescript
// BEFORE: Bugsnag metadata with onError callback
Bugsnag.notify(error, (event) => {
  event.addMetadata('order', { id: orderId, total: orderTotal });
  event.addMetadata('user', { plan: userPlan });
  event.setUser(userId, userEmail, userName);
  event.severity = 'warning';
});

// AFTER: Sentry scoped context
Sentry.withScope((scope) => {
  scope.setContext('order', { id: orderId, total: orderTotal });
  scope.setContext('user', { plan: userPlan });
  scope.setUser({ id: userId, email: userEmail, username: userName });
  scope.setLevel('warning');
  Sentry.captureException(error);
});
```

### Package Removal

```bash
# Remove all Bugsnag packages
npm uninstall @bugsnag/js @bugsnag/node @bugsnag/plugin-react \
  @bugsnag/plugin-express @bugsnag/plugin-vue @bugsnag/plugin-angular
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
