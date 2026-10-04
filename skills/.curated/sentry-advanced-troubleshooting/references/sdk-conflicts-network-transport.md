# SDK Conflicts, Network Blocks, and Custom Transport

**SDK conflicts with OpenTelemetry:**

Sentry SDK v8 uses OpenTelemetry internally. If your app also imports `@opentelemetry/*` packages directly, the two compete for the same global tracer:

```typescript
// Diagnosis: check for dual-registration
// npm ls @opentelemetry/api @opentelemetry/sdk-node @sentry/node

// If both exist, you have two options:
// Option A: Let Sentry own the OTel setup (recommended for most apps)
// Remove @opentelemetry/sdk-node, keep only @sentry/node
// Sentry auto-registers its OTel instrumentations

// Option B: Use Sentry as an OTel exporter (for teams already invested in OTel)
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  skipOpenTelemetrySetup: true, // Let your existing OTel setup control tracing
});

// Then configure SentrySpanProcessor in your OTel setup:
// tracerProvider.addSpanProcessor(new SentrySpanProcessor());
```

**SDK conflicts with winston/pino:**

Logger libraries that patch `console.*` can interfere with Sentry's console breadcrumb integration:

```typescript
// Symptom: duplicate breadcrumbs or missing log-level breadcrumbs
// Fix: disable Sentry's console integration and capture manually
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  integrations: (defaults) =>
    defaults.filter((i) => i.name !== 'Console'),
});

// In your winston transport, add Sentry breadcrumbs explicitly:
import winston from 'winston';
const sentryTransport = new winston.transports.Stream({
  stream: {
    write: (message: string) => {
      Sentry.addBreadcrumb({
        category: 'logger',
        message: message.trim(),
        level: 'info',
      });
    },
  },
});
```

**Network proxy/firewall blocking DSN endpoint:**

```bash
# Step 1: Test DNS resolution for the ingest endpoint
dig +short o0.ingest.sentry.io
# Expected: one or more IP addresses. Empty = DNS blocked.

# Step 2: Test HTTPS connectivity
curl -v --max-time 10 "https://o0.ingest.sentry.io/api/0/envelope/" 2>&1 \
  | grep -E "(HTTP/|connect to|Connection refused|timed out)"
# Expected: HTTP/2 200 or HTTP/2 403 (endpoint exists, auth required)

# Step 3: Check for corporate proxy interference
env | grep -i proxy
# If HTTP_PROXY or HTTPS_PROXY is set, Sentry may need proxy config:
# Sentry.init({ transportOptions: { proxy: process.env.HTTPS_PROXY } })

# Step 4: Bypass proxy to test direct connectivity
curl -v --proxy "" --max-time 10 https://o0.ingest.sentry.io/api/0/envelope/ 2>&1 \
  | grep "HTTP/"

# Step 5: Send a raw test envelope directly
DSN_KEY=$(echo "$SENTRY_DSN" | sed 's|.*//||' | sed 's|@.*||')
DSN_HOST=$(echo "$SENTRY_DSN" | sed 's|.*@||' | sed 's|/.*||')
PROJECT_ID=$(echo "$SENTRY_DSN" | sed 's|.*/||')

curl -X POST "https://$DSN_HOST/api/$PROJECT_ID/envelope/" \
  -H "Content-Type: application/x-sentry-envelope" \
  -H "X-Sentry-Auth: Sentry sentry_version=7, sentry_key=$DSN_KEY" \
  -d "{\"event_id\":\"$(uuidgen | tr -d '-' | head -c 32)\"}
{\"type\":\"event\"}
{\"message\":\"network diagnostic test\",\"level\":\"info\"}" \
  -w "\nHTTP Status: %{http_code}\n"
# Expected: HTTP Status 200
```

**Custom transport debugging:**

When the default transport fails (e.g., behind a corporate proxy, in serverless with short timeouts), build a diagnostic wrapper:

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  transport: (options) => {
    const baseTransport = Sentry.makeNodeTransport(options);
    return {
      send: async (envelope) => {
        const start = Date.now();
        try {
          const result = await baseTransport.send(envelope);
          console.log('[Transport] Delivered in', Date.now() - start, 'ms');
          return result;
        } catch (err) {
          console.error('[Transport] FAILED after', Date.now() - start, 'ms:', err);
          throw err;
        }
      },
      flush: (timeout) => baseTransport.flush(timeout),
    };
  },
});
```

**Comprehensive health check script:**

```bash
#!/bin/bash
# sentry-diagnose.sh — run this to get a full diagnostic snapshot
set -euo pipefail

echo "=== Sentry Diagnostic Report ==="

echo -e "\n--- Environment ---"
echo "Node.js: $(node --version 2>/dev/null || echo 'N/A')"
echo "SENTRY_DSN: $([ -n "${SENTRY_DSN:-}" ] && echo 'SET (hidden)' || echo 'MISSING')"
echo "SENTRY_RELEASE: ${SENTRY_RELEASE:-NOT SET}"
echo "SENTRY_ENVIRONMENT: ${SENTRY_ENVIRONMENT:-NOT SET}"
echo "NODE_ENV: ${NODE_ENV:-NOT SET}"

echo -e "\n--- SDK Packages ---"
npm list 2>/dev/null | grep @sentry || echo "No @sentry packages found"

echo -e "\n--- Version Alignment ---"
npm ls @sentry/core 2>/dev/null | grep @sentry/core || echo "N/A"
# Multiple versions here = version mismatch bug

echo -e "\n--- Sentry CLI ---"
sentry-cli --version 2>/dev/null || echo "CLI not installed"
sentry-cli info 2>/dev/null || echo "CLI auth not configured"

echo -e "\n--- Network ---"
curl -s -o /dev/null -w "Ingest endpoint: HTTP %{http_code} (%{time_total}s)\n" \
  --max-time 10 https://o0.ingest.sentry.io/api/0/envelope/ 2>/dev/null \
  || echo "UNREACHABLE — check firewall/proxy"

echo -e "\n--- Source Maps ---"
RELEASE="${SENTRY_RELEASE:-unknown}"
echo "Release: $RELEASE"
sentry-cli releases files "$RELEASE" list 2>/dev/null | head -10 \
  || echo "No files uploaded or auth failed"

echo -e "\n--- Proxy Detection ---"
for var in HTTP_PROXY HTTPS_PROXY NO_PROXY http_proxy https_proxy; do
  val="${!var:-}"
  [ -n "$val" ] && echo "$var=$val"
done
echo "(empty = no proxy detected)"

echo -e "\n=== Done ==="
```

## Output

- Root cause identified for silently dropped events (beforeSend, sampling, transport, tunnel)
- Source map resolution verified or mismatch pinpointed with `sourcemaps explain`
- Distributed tracing continuity confirmed across service boundaries
- Memory leak from breadcrumb accumulation diagnosed and capped
- SDK conflicts with OpenTelemetry or logging libraries resolved
- Network connectivity to Sentry ingest endpoint verified or proxy identified
- Custom transport instrumented with timing and error logging

## Error Handling

| Symptom | Root Cause | Solution |
|---------|-----------|----------|
| `debug: true` prints nothing | SDK never initialized | Verify `instrument.mjs` loads via `--import` flag before app code |
| `flush()` always times out | Network blocking outbound HTTPS | Check firewall rules, proxy env vars; test with `curl` to ingest endpoint |
| Source maps show wrong file | URL prefix does not match stack frame URL | Run `sentry-cli sourcemaps explain EVENT_ID` to see exact mismatch |
| Duplicate events in dashboard | Multiple `Sentry.init()` calls in codebase | Search for all init calls (`grep -r "Sentry.init"`), consolidate to one file |
| Heap grows steadily over hours | Unbounded breadcrumb accumulation | Set `maxBreadcrumbs: 20`, filter noisy console integrations |
| Traces split into separate transactions | Missing propagation headers to downstream | Verify `tracePropagationTargets` includes the downstream service URL |
| `Sentry.getActiveSpan()` returns undefined | HTTP call is outside a span context | Wrap the call in `Sentry.startSpan()` or check async context propagation |
| OpenTelemetry double-tracing | Both Sentry and OTel register global tracer | Use `skipOpenTelemetrySetup: true` and add `SentrySpanProcessor` to your OTel SDK |

## Examples

**TypeScript — Full diagnostic init for a production Node.js service:**

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV || 'development',
  release: process.env.SENTRY_RELEASE,
  debug: process.env.SENTRY_DEBUG === 'true',
  maxBreadcrumbs: 30,
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.2 : 1.0,
  tracePropagationTargets: [
    'localhost',
    /^https:\/\/api\.yourapp\.com/,
    /^https:\/\/internal\./,
  ],
  beforeSend(event, hint) {
    // Log every event decision for troubleshooting
    if (process.env.SENTRY_DEBUG === 'true') {
      console.log('[Sentry beforeSend]', {
        type: event.type,
        message: event.message,
        exception: hint?.originalException?.constructor?.name,
      });
    }
    return event;
  },
  integrations: (defaults) => [
    ...defaults,
    Sentry.consoleIntegration({ levels: ['error', 'warn'] }),
  ],
});

// Verify and log SDK state at startup
const client = Sentry.getClient();
if (client) {
  const dsn = client.getDsn();
  console.log('[Sentry] Initialized:', {
    host: dsn?.host,
    project: dsn?.projectId,
    release: client.getOptions().release,
    integrations: client.getOptions().integrations?.map((i) => i.name),
  });
} else {
  console.error('[Sentry] CRITICAL: Client failed to initialize');
}
```

**Python — Diagnostic init with event logging:**

```python
import sentry_sdk
import os
import logging

logger = logging.getLogger("sentry_debug")

def before_send_debug(event, hint):
    """Log every event decision for troubleshooting."""
    exc = hint.get("exc_info")
    logger.info(
        "[Sentry beforeSend] type=%s exception=%s message=%s",
        event.get("type", "error"),
        exc[0].__name__ if exc else "none",
        event.get("message", ""),
    )
    return event

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("SENTRY_ENVIRONMENT", "development"),
    release=os.environ.get("SENTRY_RELEASE"),
    traces_sample_rate=0.2,
    max_breadcrumbs=30,
    debug=os.environ.get("SENTRY_DEBUG", "").lower() == "true",
    before_send=before_send_debug,
    # Propagate traces only to your own services
    trace_propagation_targets=[
        r"^https://api\.yourapp\.com",
        r"^https://internal\.",
        "localhost",
    ],
)

# Verify initialization
client = sentry_sdk.get_client()
if client.is_active():
    logger.info("[Sentry] SDK active — DSN project: %s", client.dsn.split("/")[-1])
    # Fire test event
    event_id = sentry_sdk.capture_message("Diagnostic probe", level="debug")
    logger.info("[Sentry] Test event: %s", event_id)
    sentry_sdk.flush(timeout=5)
else:
    logger.error("[Sentry] SDK is NOT active — check DSN and init order")
```

## Resources

- [Troubleshooting Guide](https://docs.sentry.io/platforms/javascript/troubleshooting/)
- [Source Maps Troubleshooting](https://docs.sentry.io/platforms/javascript/sourcemaps/troubleshooting_js/)
- Source Maps Explain Command
- [Distributed Tracing](https://docs.sentry.io/platforms/javascript/tracing/trace-propagation/)
- [Transport Configuration](https://docs.sentry.io/platforms/javascript/configuration/transports/)
- OpenTelemetry Integration
- [Python SDK Troubleshooting](https://docs.sentry.io/platforms/python/troubleshooting/)

## Next Steps

- **sentry-performance-tracing** — Deep dive into span instrumentation and custom transactions
- **sentry-release-management** — Automate release tracking and source map uploads in CI
- **sentry-ci-integration** — Wire Sentry into your CI pipeline for deploy notifications
- **sentry-common-errors** — Quick reference for the most frequent Sentry SDK error messages
