# Integration Pitfalls

## Pitfall 5: Release Version Mismatch Between SDK and Source Maps

Sentry matches error stack frames to source maps using the `release` field. If SDK and CLI use different release strings, source maps never apply and you get minified traces.

```typescript
// WRONG — version mismatch
// SDK:  Sentry.init({ release: "1.2.3" })
// CLI:  sentry-cli releases new "v1.2.3"   (note the "v" prefix)

// RIGHT — single source of truth
const SENTRY_RELEASE = `myapp@${process.env.GIT_SHA}`;
Sentry.init({ release: SENTRY_RELEASE });
```

```bash
# CI — same variable for SDK and CLI
export SENTRY_RELEASE="myapp@$(git rev-parse --short HEAD)"
npx sentry-cli releases new "$SENTRY_RELEASE"
npx sentry-cli sourcemaps upload --release="$SENTRY_RELEASE" --url-prefix="~/static/js" ./dist/
npx sentry-cli releases finalize "$SENTRY_RELEASE"
```

## Pitfall 9: Ignoring `429 Too Many Requests`

When quota is exceeded, Sentry returns 429 and the SDK silently drops events. Without monitoring, you lose data during peak traffic.

```typescript
// Prevention: enable spike protection
// Sentry Dashboard > Settings > Spike Protection > Enable

// Client-side: circuit breaker pattern
let sentryDisabled = false;
let disabledUntil = 0;

Sentry.init({
  beforeSend(event) {
    if (sentryDisabled && Date.now() < disabledUntil) return null;
    sentryDisabled = false;
    return event;
  },
});
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
