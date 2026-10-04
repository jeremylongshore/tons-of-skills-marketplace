---
name: sentry-advanced-troubleshooting
description: 'Advanced Sentry troubleshooting for complex SDK issues, silent event
  drops,

  source map failures, distributed tracing gaps, and SDK conflicts.

  Use when events silently disappear, source maps fail to resolve,

  traces break across service boundaries, or the SDK conflicts with

  other libraries like OpenTelemetry or winston.

  Trigger with phrases like "sentry events missing", "sentry source maps broken",

  "sentry debug", "sentry not capturing errors", "sentry tracing gaps",

  "sentry memory leak", "sentry sdk conflict".

  '
allowed-tools: Read, Write, Edit, Grep, Bash(node:*), Bash(npm:*), Bash(npx:*), Bash(curl:*),
  Bash(sentry-cli:*), Bash(dig:*)
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- debugging
- troubleshooting
- source-maps
- distributed-tracing
- sdk-conflicts
compatibility: Designed for Claude Code
---
# Sentry Advanced Troubleshooting

## Overview

This skill addresses complex Sentry issues that go beyond basic setup: events that silently drop, source maps that refuse to resolve, distributed traces with gaps between services, SDK memory leaks, conflicts with other observability libraries, and network-level DSN blocking. Each section provides a systematic diagnosis path with concrete commands and code to identify root causes.

## Prerequisites

- Sentry SDK v8 installed and initialized (see `sentry-install-auth` skill)
- Access to application logs, Sentry dashboard, and project settings
- Sentry CLI installed (`npm install -g @sentry/cli`) for source map debugging
- Network diagnostic tools available (curl, dig)
- `debug: true` enabled in SDK init for verbose console output during troubleshooting

## Instructions

### Step 1 — Diagnose Silently Dropped Events

Events can vanish at multiple points between your code and the Sentry dashboard. Work through each layer systematically.

**Enable debug mode to see SDK internals:**

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  debug: true, // Prints all SDK decisions to console

  // Wrap transport to log every outbound envelope
  transport: (options) => {
    const transport = Sentry.makeNodeTransport(options);
    return {
      ...transport,
      send: async (envelope) => {
        const [header, items] = envelope;
        console.log('[Sentry Transport] Outbound envelope:', {
          event_id: header.event_id,
          sent_at: header.sent_at,
          item_count: items?.length,
        });
        const result = await transport.send(envelope);
        console.log('[Sentry Transport] Response:', result);
        return result;
      },
    };
  },
});
```

**Systematic event-drop diagnosis:**

```typescript
async function diagnoseEventDrop(): Promise<void> {
  // Layer 1: Is the client alive?
  const client = Sentry.getClient();
  if (!client) {
    console.error('FAIL: Sentry client is null — SDK never initialized');
    console.error('Check: Is instrument.mjs loaded via --import flag?');
    return;
  }

  // Layer 2: Is the DSN valid and reachable?
  const dsn = client.getDsn();
  if (!dsn) {
    console.error('FAIL: DSN is null — check SENTRY_DSN env var');
    return;
  }
  console.log('DSN:', `${dsn.protocol}://${dsn.host}/${dsn.projectId}`);

  // Layer 3: Is beforeSend silently dropping events?
  const opts = client.getOptions();
  if (opts.beforeSend) {
    console.warn('WARN: beforeSend is configured — it may be returning null');
    console.warn('Test by temporarily removing beforeSend to isolate');
  }

  // Layer 4: Is sampling dropping events?
  console.log('sampleRate:', opts.sampleRate ?? '1.0 (default)');
  console.log('tracesSampleRate:', opts.tracesSampleRate ?? 'not set');
  if (opts.sampleRate === 0) {
    console.error('FAIL: sampleRate is 0 — ALL error events are dropped');
  }

  // Layer 5: Fire a test event and verify delivery
  const eventId = Sentry.captureMessage('Diagnostic probe — safe to ignore', 'debug');
  console.log('Test event ID:', eventId || 'NONE — event was dropped before send');

  // Layer 6: Flush the transport buffer
  const flushed = await Sentry.flush(10000);
  console.log('Flush result:', flushed ? 'SUCCESS' : 'TIMEOUT — likely network issue');
  if (!flushed) {
    console.error('Events are queued but cannot reach Sentry — check network/proxy');
  }
}
```

**Check for tunnel misconfiguration:**

If you route events through a server-side tunnel (to bypass ad blockers), verify the tunnel endpoint proxies correctly:

```bash
# Test your tunnel endpoint returns 200 and forwards to Sentry
curl -v -X POST "https://yourapp.com/api/sentry-tunnel" \
  -H "Content-Type: application/x-sentry-envelope" \
  -d '{"dsn":"https://key@o0.ingest.sentry.io/123"}
{"type":"event"}
{"message":"tunnel test","level":"info"}' 2>&1 | grep "< HTTP"
# Expected: HTTP/2 200 (or 202)
```

### Step 2 — Debug Source Maps, Distributed Tracing, and Memory Leaks

**Source map resolution failures:**

Source maps break when the artifact URL stored in Sentry does not match the URL in the error's stack frame. Use `sentry-cli sourcemaps explain` to pinpoint the exact mismatch:

```bash
# List artifacts uploaded for the current release
RELEASE="${SENTRY_RELEASE:-$(node -e "console.log(require('./package.json').version)")}"
echo "Checking release: $RELEASE"
sentry-cli releases files "$RELEASE" list

# Explain why a specific event has unresolved source maps
# Get the event ID from the Sentry issue detail page
sentry-cli sourcemaps explain \
  --org "$SENTRY_ORG" \
  --project "$SENTRY_PROJECT" \
  "EVENT_ID_HERE"

# Common output: "artifact ~/static/js/main.abc123.js not found"
# This means your url-prefix does not match the deployed URL path
```

**Validate before uploading:**

```bash
# Dry-run upload to catch issues before they affect production
sentry-cli sourcemaps upload \
  --release="$RELEASE" \
  --url-prefix="~/static/js" \
  --validate \
  --dry-run \
  ./dist

# If using a bundler plugin, verify it sets the correct prefix:
# Webpack: devtool: 'source-map' (not 'eval-source-map')
# Vite: build.sourcemap: true
```

**Check the URL matching rule:** The stack frame URL (e.g., `https://example.com/static/js/main.abc123.js`) must match the artifact URL (e.g., `~/static/js/main.abc123.js`) after the tilde prefix substitution. If your CDN rewrites paths, the prefix must account for the rewritten path.

**Distributed tracing gaps:**

When traces break between services (a parent service starts a trace but the downstream service creates a new unlinked trace), the issue is missing propagation headers:

```typescript
// Verify propagation headers are being sent
// In your HTTP client (axios, fetch, etc.), log outbound headers:

import * as Sentry from '@sentry/node';

// Check: does the active span exist when the outbound call happens?
const activeSpan = Sentry.getActiveSpan();
if (!activeSpan) {
  console.error('No active span at the point of outbound HTTP call');
  console.error('The call must happen INSIDE a Sentry.startSpan() callback');
}

// Manually propagate if auto-instrumentation is not working
const headers: Record<string, string> = {};
Sentry.getClient()?.getOptions().tracePropagationTargets; // check targets
console.log('tracePropagationTargets:',
  Sentry.getClient()?.getOptions().tracePropagationTargets ?? 'default (all)');

// Verify: the downstream service must extract these headers
// sentry-trace: <traceId>-<spanId>-<sampled>
// baggage: sentry-environment=production,sentry-release=1.0.0,...
```

```typescript
// Fix: ensure tracePropagationTargets includes the downstream URL
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 1.0,
  // Only propagate to your own services — never to third-party APIs
  tracePropagationTargets: [
    'localhost',
    /^https:\/\/api\.yourapp\.com/,
    /^https:\/\/internal\./,
  ],
});
```

**Memory leak from unbounded breadcrumbs:**

The SDK stores breadcrumbs in memory. In long-running processes (workers, daemons), unbounded accumulation causes heap growth:

```typescript
// Diagnosis: check breadcrumb count over time
setInterval(() => {
  const scope = Sentry.getCurrentScope();
  // @ts-expect-error — accessing internal for diagnosis only
  const breadcrumbs = scope._breadcrumbs?.length ?? 'unknown';
  const mem = process.memoryUsage();
  console.log('[Sentry Health]', {
    breadcrumbs,
    heapUsed: `${(mem.heapUsed / 1024 / 1024).toFixed(1)} MB`,
    rss: `${(mem.rss / 1024 / 1024).toFixed(1)} MB`,
  });
}, 60_000);

// Fix: cap breadcrumbs and disable noisy auto-breadcrumbs
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  maxBreadcrumbs: 20, // Default is 100 — reduce for long-running processes
  integrations: [
    // Disable console breadcrumbs if they flood the buffer
    Sentry.consoleIntegration({ levels: ['error', 'warn'] }),
  ],
});
```

### Step 3 — Resolve SDK Conflicts, Network Blocks, and Custom Transport Issues

See [SDK conflicts, network blocks, and custom transport](references/sdk-conflicts-network-transport.md) for OpenTelemetry dual-registration fixes, winston/pino conflict resolution, network proxy/firewall diagnosis (DNS, curl, raw envelope test), custom transport debugging wrappers, and a comprehensive diagnostic shell script.

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
