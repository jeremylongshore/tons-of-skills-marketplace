# Examples

## Example 1: Debug Missing Events in Next.js

**Request:** "Sentry captureException runs but nothing shows in the dashboard"

**Diagnosis:**

1. Enabled `debug: true` in `sentry.client.config.ts`
2. Console showed: `[Sentry] No DSN provided, will not send event`
3. `NEXT_PUBLIC_SENTRY_DSN` was missing from `.env.production`

**Fix:** Added the DSN to `.env.production` and redeployed.
**Result:** Events appeared within seconds.

## Example 2: Fix Source Maps in Vite + React

**Request:** "Stack traces in Sentry are all minified"

**Diagnosis:**

```bash
sentry-cli sourcemaps explain --org acme --project frontend EVENT_ID
# Output: "source map not found for URL ~/assets/index-abc123.js"
```

The `--url-prefix` was `~/dist` but Vite serves from `~/assets`.

**Fix:** Changed to `--url-prefix '~/assets'` and re-uploaded.
**Result:** Stack traces now show original source locations.

## Example 3: Lambda Events Disappearing

**Request:** "Sentry.captureException works locally but not in AWS Lambda"

**Diagnosis:** Lambda exits before the SDK's async queue flushes.

**Fix:** Added `await Sentry.flush(2000)` and wrapped with `Sentry.wrapHandler()`.
**Result:** Events arrive consistently from Lambda.

## Example 4: 429 Rate Limiting in Production

**Request:** "Sentry returning 429 errors, losing important error data"

**Diagnosis:** Noisy `ResizeObserver` and `ChunkLoadError` events consuming 80% of quota.

**Fix:** Added `ignoreErrors` for noise + `beforeSend` filter for browser extension errors.
**Result:** Event volume dropped 75%, no more 429 errors.

## Example 5: Express Import Order Fix

**Request:** "Getting 'Express is not instrumented' warning"

**Diagnosis:** `Sentry.init()` was at the bottom of `app.ts`, after all imports.

**Fix:** Created `instrument.mjs` with Sentry init, imported first in `app.mjs`.
**Result:** Warning gone, Express routes show in Performance tab.

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
