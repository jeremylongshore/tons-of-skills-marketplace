# Examples

**Example 1: Full-stack audit**
Request: "Audit our Sentry setup for common mistakes"
Result: Found hardcoded DSN (Pitfall 1), 100% tracesSampleRate (Pitfall 2), no environment tag (Pitfall 7), and zero alert rules (Pitfall 10). Applied fixes for all four, added CI gate, created three-tier alert config.

**Example 2: Missing Lambda errors**
Request: "Sentry shows no errors from Lambda but we know they're failing"
Result: No `flush()` call (Pitfall 3). Wrapped handlers with `Sentry.wrapHandler()` from `@sentry/aws-serverless`. Events appear within 5 seconds.

**Example 3: Minified stack traces**
Request: "Source maps uploaded but stack traces are still minified"
Result: SDK release `2.1.0` vs CLI release `v2.1.0` (Pitfall 5). Unified to `$GIT_SHA` via shared `SENTRY_RELEASE` env var.

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
