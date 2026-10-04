# Migration From Rollbar

## Concept Mapping: Rollbar to Sentry

Rollbar uses "items" and "occurrences" where Sentry uses "issues" and "events." A Rollbar "item" groups related occurrences by fingerprint, equivalent to a Sentry "issue" grouping events.

### SDK Replacement (Node.js)

```typescript
// BEFORE: Rollbar initialization
import Rollbar from 'rollbar';
const rollbar = new Rollbar({
  accessToken: process.env.ROLLBAR_TOKEN,
  environment: process.env.NODE_ENV,
  codeVersion: process.env.npm_package_version,
  nodeSourceMaps: true,
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

| Rollbar | Sentry | Notes |
|---------|--------|-------|
| `rollbar.error(err)` | `Sentry.captureException(err)` | Direct replacement |
| `rollbar.error(msg, err)` | `Sentry.captureException(err)` | Message becomes event title |
| `rollbar.warning(msg)` | `Sentry.captureMessage(msg, 'warning')` | Second arg sets severity |
| `rollbar.info(msg)` | `Sentry.captureMessage(msg, 'info')` | Appears in breadcrumbs trail |
| `rollbar.debug(msg)` | `Sentry.captureMessage(msg, 'debug')` | Usually filtered by `beforeSend` |
| `rollbar.configure({ person: { id, email } })` | `Sentry.setUser({ id, email })` | Call once after auth |
| `rollbar.configure({ payload: { custom: data } })` | `Sentry.setContext('custom', data)` | Appears in event context tab |
| `rollbar.configure({ code_version })` | `Sentry.init({ release })` | Set at init time |
| `rollbar.configure({ checkIgnore: fn })` | `Sentry.init({ beforeSend: fn })` | Return null to drop event |
| Custom fingerprinting via `rollbar.error(msg, { fingerprint })` | `Sentry.withScope(s => { s.setFingerprint([...]) })` | Controls issue grouping |

### Express Middleware Migration

```typescript
// BEFORE: Rollbar Express middleware
import Rollbar from 'rollbar';
const rollbar = new Rollbar({ accessToken: process.env.ROLLBAR_TOKEN });
app.use(rollbar.errorHandler());

// AFTER: Sentry Express middleware (v8+)
import * as Sentry from '@sentry/node';
Sentry.init({ dsn: process.env.SENTRY_DSN });
Sentry.setupExpressErrorHandler(app);
```

### Data Export

Export historical Rollbar data for reference (data does not import into Sentry, but provides context):

```bash
# Export recent items via Rollbar API
curl -s -H "X-Rollbar-Access-Token: $ROLLBAR_TOKEN" \
  "https://api.rollbar.com/api/1/items?status=active&level=error" \
  | jq '.result.items[] | {title: .title, total_occurrences: .total_occurrences, last_occurrence: .last_occurrence_timestamp}' \
  > rollbar-export.json
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
