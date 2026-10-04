---
name: sentry-debug-bundle
description: 'Collect diagnostic information for Sentry troubleshooting and support
  tickets.

  Use when events are not appearing in Sentry, SDK initialization seems broken,

  DSN connectivity fails, source maps are not resolving, or preparing a support request.

  Trigger with "sentry debug info", "sentry diagnostics", "debug bundle", "sentry
  support ticket".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(node:*), Bash(npx:*), Bash(pip:*),
  Bash(python:*), Bash(curl:*), Bash(dig:*), Bash(sentry-cli:*), Grep, Glob
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- debugging
- support
- diagnostics
compatibility: Designed for Claude Code
---
# Sentry Debug Bundle

## Overview

Collect SDK versions, configuration state, network connectivity, and event delivery status into a single diagnostic report. Attach the output to Sentry support tickets or use it to systematically isolate why events are not reaching the dashboard.

## Current State

!`node --version 2>/dev/null || echo 'Node.js not found'`
!`python3 --version 2>/dev/null || echo 'Python3 not found'`
!`npm list @sentry/node @sentry/browser @sentry/react @sentry/cli 2>/dev/null | grep sentry || pip show sentry-sdk 2>/dev/null | grep -E '^(Name|Version)' || echo 'No Sentry SDK found'`
!`sentry-cli --version 2>/dev/null || echo 'sentry-cli not installed'`
!`sentry-cli info 2>/dev/null || echo 'sentry-cli not authenticated'`

## Prerequisites

- At least one Sentry SDK installed (`@sentry/node`, `@sentry/browser`, `@sentry/react`, or `sentry-sdk` for Python)
- `SENTRY_DSN` environment variable set (or DSN configured in application code)
- For API checks: `SENTRY_AUTH_TOKEN` with `project:read` scope ([generate token](https://sentry.io/settings/auth-tokens/))
- Optional: `sentry-cli` installed for source map diagnostics and `send-event` tests

## Instructions

### Step 1 — Gather SDK Version, Configuration, and Init Hooks

Identify the installed SDK, verify all `@sentry/*` packages share the same version (mismatches cause silent failures), and extract the runtime configuration.

**Check installed packages:**

```bash
# Node.js — list all Sentry packages and flag version mismatches
npm ls @sentry/node @sentry/browser @sentry/react @sentry/nextjs @sentry/cli 2>/dev/null | grep sentry

# Python — show sentry-sdk version and installed extras
pip show sentry-sdk 2>/dev/null
```

**Extract runtime configuration (Node.js):**

```typescript
import * as Sentry from '@sentry/node';

const client = Sentry.getClient();
if (!client) {
  console.error('ERROR: Sentry client not initialized — Sentry.init() may not have been called');
  process.exit(1);
}

const opts = client.getOptions();
const diagnostics = {
  sdk_version: Sentry.SDK_VERSION,
  dsn_configured: !!opts.dsn,
  dsn_host: opts.dsn ? new URL(opts.dsn).hostname : 'N/A',
  dsn_project_id: opts.dsn ? new URL(opts.dsn).pathname.replace('/', '') : 'N/A',
  environment: opts.environment ?? '(default)',
  release: opts.release ?? '(auto-detect)',
  debug: opts.debug ?? false,
  sample_rate: opts.sampleRate ?? 1.0,
  traces_sample_rate: opts.tracesSampleRate ?? '(not set)',
  profiles_sample_rate: opts.profilesSampleRate ?? '(not set)',
  send_default_pii: opts.sendDefaultPii ?? false,
  max_breadcrumbs: opts.maxBreadcrumbs ?? 100,
  before_send: typeof opts.beforeSend === 'function' ? 'CONFIGURED' : 'none',
  before_send_transaction: typeof opts.beforeSendTransaction === 'function' ? 'CONFIGURED' : 'none',
  before_breadcrumb: typeof opts.beforeBreadcrumb === 'function' ? 'CONFIGURED' : 'none',
  integrations: client.getOptions().integrations?.map(i => i.name) ?? [],
  transport: opts.transport ? 'custom' : 'default',
};

console.log(JSON.stringify(diagnostics, null, 2));
```

**Extract runtime configuration (Python):**

```python
import sentry_sdk
from sentry_sdk import Hub

client = Hub.current.client
if not client:
    print("ERROR: Sentry client not initialized")
    exit(1)

opts = client.options
print(f"SDK version:       {sentry_sdk.VERSION}")
print(f"DSN configured:    {bool(opts.get('dsn'))}")
print(f"Environment:       {opts.get('environment', '(default)')}")
print(f"Release:           {opts.get('release', '(auto-detect)')}")
print(f"Debug:             {opts.get('debug', False)}")
print(f"Sample rate:       {opts.get('sample_rate', 1.0)}")
print(f"Traces sample rate:{opts.get('traces_sample_rate', '(not set)')}")
print(f"Send default PII:  {opts.get('send_default_pii', False)}")
print(f"before_send:       {'CONFIGURED' if opts.get('before_send') else 'none'}")
print(f"before_breadcrumb: {'CONFIGURED' if opts.get('before_breadcrumb') else 'none'}")
print(f"Integrations:      {[i.identifier for i in client.integrations.values()]}")
```

> **Key check:** If `beforeSend` is CONFIGURED, inspect the function — a `beforeSend` that returns `null` will silently drop every event.

### Step 2 — Verify DSN Connectivity and Sentry Service Status

Confirm the application can reach Sentry's ingest endpoint and that Sentry itself is operational.

**Test DSN reachability:**

```bash
# Test the Sentry API root (should return HTTP 200)
curl -s -o /dev/null -w "sentry.io API: HTTP %{http_code} (%{time_total}s)\n" \
  https://sentry.io/api/0/

# Test the ingest endpoint derived from your DSN
# DSN format: https://<PUBLIC_KEY>@o<ORG_ID>.ingest.sentry.io/<PROJECT_ID>
# Extract host from DSN and test the envelope endpoint
curl -s -o /dev/null -w "Ingest endpoint: HTTP %{http_code} (%{time_total}s)\n" \
  "https://o0.ingest.sentry.io/api/0/envelope/"

# DNS resolution check
dig +short o0.ingest.sentry.io 2>/dev/null || nslookup o0.ingest.sentry.io

# Check for proxy/firewall interference
curl -v https://sentry.io/api/0/ 2>&1 | grep -iE 'proxy|blocked|forbidden|connect'
```

**Check Sentry service status:**

Visit [https://status.sentry.io](https://status.sentry.io) or:

```bash
# Programmatic status check
curl -s https://status.sentry.io/api/v2/status.json | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"Sentry Status: {d['status']['description']}\")
print(f\"Updated:       {d['page']['updated_at']}\")
"
```

**Verify auth token and project access (requires `SENTRY_AUTH_TOKEN`):**

```bash
# Check token validity and list accessible projects
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  https://sentry.io/api/0/projects/ | python3 -c "
import sys, json
projects = json.load(sys.stdin)
if isinstance(projects, dict) and 'detail' in projects:
    print(f'Auth error: {projects[\"detail\"]}')
else:
    for p in projects[:10]:
        print(f\"  {p['organization']['slug']}/{p['slug']} (platform: {p.get('platform', 'N/A')})\")"

# sentry-cli auth check
sentry-cli info 2>/dev/null || echo "sentry-cli not authenticated — run: sentry-cli login"
```

### Step 3 — Test Event Capture, Verify Delivery, and Generate Report

Send a diagnostic test event, confirm it arrives in Sentry, and produce the final debug bundle report.

**Send test event via sentry-cli:**

```bash
# Quick test — sends a test message event
sentry-cli send-event -m "diagnostic test from debug-bundle $(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

**Send test event programmatically (Node.js):**

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  debug: true, // Enables console logging of SDK internals
});

const eventId = Sentry.captureMessage('sentry-debug-bundle diagnostic test', 'info');
console.log(`Test event ID: ${eventId}`);
console.log(`View at: https://sentry.io/organizations/YOUR_ORG/issues/?query=${eventId}`);

// CRITICAL: Node.js will exit before async transport completes without flush
const flushed = await Sentry.flush(10000);
console.log(`Flush: ${flushed ? 'SUCCESS — event delivered' : 'TIMEOUT — event may not have been sent'}`);

if (!flushed) {
  console.error('Flush timeout. Possible causes:');
  console.error('  - Network blocking outbound HTTPS to sentry.io');
  console.error('  - DSN is invalid or project has been deleted');
  console.error('  - Rate limit exceeded (HTTP 429)');
}
```

**Send test event programmatically (Python):**

```python
import sentry_sdk
import time

sentry_sdk.init(dsn="YOUR_DSN", debug=True)

event_id = sentry_sdk.capture_message("sentry-debug-bundle diagnostic test", level="info")
print(f"Test event ID: {event_id}")

# Python SDK flushes automatically on exit, but explicit flush is safer
sentry_sdk.flush(timeout=10)
print("Flush complete — check Sentry dashboard for event")
```

**Generate the debug bundle report:**

```bash
#!/bin/bash
set -euo pipefail

REPORT="sentry-debug-$(date +%Y%m%d-%H%M%S).md"

cat > "$REPORT" << 'HEADER'
# Sentry Debug Bundle
HEADER

cat >> "$REPORT" << EOF
**Generated:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")
**Node.js:** $(node --version 2>/dev/null || echo N/A)
**Python:** $(python3 --version 2>/dev/null || echo N/A)
**OS:** $(uname -srm)
**sentry-cli:** $(sentry-cli --version 2>/dev/null || echo 'not installed')

## SDK Packages
\`\`\`
$(npm list 2>/dev/null | grep -i sentry || echo "No npm Sentry packages")
$(pip show sentry-sdk 2>/dev/null | grep -E '^(Name|Version|Location)' || echo "No pip sentry-sdk")
\`\`\`

## Environment Variables (sanitized)
| Variable | Status |
|----------|--------|
| SENTRY_DSN | $([ -n "${SENTRY_DSN:-}" ] && echo "SET (\`$(echo "$SENTRY_DSN" | sed 's|//[^@]*@|//***@|')\`)" || echo "NOT SET") |
| SENTRY_ORG | ${SENTRY_ORG:-NOT SET} |
| SENTRY_PROJECT | ${SENTRY_PROJECT:-NOT SET} |
| SENTRY_AUTH_TOKEN | $([ -n "${SENTRY_AUTH_TOKEN:-}" ] && echo "SET (${#SENTRY_AUTH_TOKEN} chars)" || echo "NOT SET") |
| SENTRY_RELEASE | ${SENTRY_RELEASE:-NOT SET} |
| SENTRY_ENVIRONMENT | ${SENTRY_ENVIRONMENT:-NOT SET} |
| NODE_ENV | ${NODE_ENV:-NOT SET} |

## Network Connectivity
$(curl -s -o /dev/null -w "- sentry.io API: HTTP %{http_code} (%{time_total}s)" https://sentry.io/api/0/ 2>/dev/null || echo "- sentry.io: UNREACHABLE")
$(curl -s -o /dev/null -w "\n- Ingest endpoint: HTTP %{http_code} (%{time_total}s)" https://o0.ingest.sentry.io/api/0/envelope/ 2>/dev/null || echo "- Ingest: UNREACHABLE")

## Sentry Status
$(curl -s https://status.sentry.io/api/v2/status.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"- Status: {d['status']['description']}\")" 2>/dev/null || echo "- Status: Could not fetch")

## CLI Authentication Status
\`\`\`
$(sentry-cli info 2>/dev/null || echo "sentry-cli not authenticated — run: sentry-cli login")
\`\`\`

## Source Map Artifacts
\`\`\`
$(sentry-cli releases files "${SENTRY_RELEASE:-unknown}" list 2>/dev/null || echo "No release artifacts found (set SENTRY_RELEASE)")
\`\`\`
EOF

echo "Debug bundle saved to: $REPORT"
echo "Attach this file to your Sentry support ticket at https://sentry.io/support/"
```

## Output

The debug bundle produces:

- **SDK inventory** — all `@sentry/*` or `sentry-sdk` versions with mismatch detection
- **Configuration snapshot** — DSN (redacted), environment, release, sample rates, hooks status
- **Connectivity report** — HTTP status and latency to `sentry.io` API and ingest endpoints
- **Service status** — current Sentry platform health from status.sentry.io
- **Test event confirmation** — event ID with flush result (SUCCESS or TIMEOUT)
- **Markdown report file** — `sentry-debug-YYYYMMDD-HHMMSS.md` ready to attach to support tickets

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Sentry client not initialized` | `Sentry.init()` not called or called after diagnostic code | Ensure `Sentry.init()` runs at application entry point before any capture calls |
| `Flush: TIMEOUT` | Network blocking outbound HTTPS to `*.ingest.sentry.io` | Check firewall rules, corporate proxy, VPN — allow outbound 443 to `*.ingest.sentry.io` |
| `sentry-cli info` reports no auth | Token not set or expired | Run `sentry-cli login` or set `SENTRY_AUTH_TOKEN` ([generate](https://sentry.io/settings/auth-tokens/)) |
| Package version mismatch (`@sentry/*` at different versions) | Partial upgrade or transitive dependency conflict | Align all `@sentry/*` packages to the same version: `npm i @sentry/node@latest @sentry/browser@latest` and run `npm dedupe` |
| `sourcemaps explain` shows no match | `--url-prefix` does not match the stack trace URLs | Compare the `abs_path` in your error event's stack frame with the `--url-prefix` used during upload |
| Events dropped by `beforeSend` | Hook returns `null` for matching events | Log inside `beforeSend` to verify: `console.log('beforeSend:', event.exception?.values?.[0]?.type)` |
| DSN returns HTTP 401 / 403 | Project deleted, DSN revoked, or wrong organization | Verify DSN at Settings > Projects > Client Keys in the Sentry dashboard |
| `429 Too Many Requests` | Organization or project rate limit exceeded | Check quotas at Settings > Subscription, reduce `sampleRate`/`tracesSampleRate`, or use `beforeSend` to filter noise |
| Process exits before events sent (Node.js) | No `await Sentry.flush()` before `process.exit()` | Always call `await Sentry.flush(timeout)` before exiting; in serverless, use the platform's `Sentry.wrapHandler()` |

## Examples

### TypeScript — Full Diagnostic Script

```typescript
// scripts/sentry-diagnostics.ts
import * as Sentry from '@sentry/node';

async function runDiagnostics() {
  // 1. Check SDK is initialized
  const client = Sentry.getClient();
  if (!client) {
    console.error('[FAIL] Sentry client not initialized');
    console.error('       Ensure Sentry.init({ dsn: "..." }) is called before this script');
    return;
  }
  console.log(`[OK]   SDK version: ${Sentry.SDK_VERSION}`);

  // 2. Check configuration
  const opts = client.getOptions();
  console.log(`[OK]   DSN configured: ${!!opts.dsn}`);
  console.log(`[INFO] Environment: ${opts.environment ?? '(default)'}`);
  console.log(`[INFO] Release: ${opts.release ?? '(auto-detect)'}`);
  console.log(`[INFO] Debug mode: ${opts.debug ?? false}`);
  console.log(`[INFO] Sample rate: ${opts.sampleRate ?? 1.0}`);
  console.log(`[INFO] Traces sample rate: ${opts.tracesSampleRate ?? '(not set)'}`);
  console.log(`[INFO] beforeSend: ${typeof opts.beforeSend === 'function' ? 'CONFIGURED' : 'none'}`);

  // 3. List active integrations
  const integrations = opts.integrations?.map(i => i.name) ?? [];
  console.log(`[INFO] Integrations (${integrations.length}): ${integrations.join(', ')}`);

  // 4. Send test event
  const eventId = Sentry.captureMessage('sentry-diagnostics test event', 'info');
  console.log(`[INFO] Test event ID: ${eventId}`);

  // 5. Flush and verify
  const flushed = await Sentry.flush(10000);
  if (flushed) {
    console.log('[OK]   Flush succeeded — event delivered to Sentry');
  } else {
    console.error('[FAIL] Flush timed out — check network connectivity to Sentry');
  }
}

runDiagnostics().catch(err => console.error('[FAIL] Diagnostic error:', err));
```

### Python — Full Diagnostic Script

```python
# scripts/sentry_diagnostics.py
import sentry_sdk
from sentry_sdk import Hub
import urllib.request
import json
import sys

def run_diagnostics():
    print("=== Sentry Debug Bundle (Python) ===\n")

    # 1. SDK version
    print(f"SDK version: {sentry_sdk.VERSION}")

    # 2. Client check
    client = Hub.current.client
    if not client:
        print("[FAIL] Sentry client not initialized")
        print("       Call sentry_sdk.init(dsn='...') before running diagnostics")
        sys.exit(1)
    print("[OK]   Client initialized")

    # 3. Configuration
    opts = client.options
    print(f"[INFO] DSN configured: {bool(opts.get('dsn'))}")
    print(f"[INFO] Environment: {opts.get('environment', '(default)')}")
    print(f"[INFO] Release: {opts.get('release', '(auto-detect)')}")
    print(f"[INFO] Debug: {opts.get('debug', False)}")
    print(f"[INFO] Sample rate: {opts.get('sample_rate', 1.0)}")
    print(f"[INFO] Traces sample rate: {opts.get('traces_sample_rate', '(not set)')}")
    print(f"[INFO] before_send: {'CONFIGURED' if opts.get('before_send') else 'none'}")
    print(f"[INFO] before_breadcrumb: {'CONFIGURED' if opts.get('before_breadcrumb') else 'none'}")

    # 4. Integrations
    integrations = [i.identifier for i in client.integrations.values()]
    print(f"[INFO] Integrations ({len(integrations)}): {', '.join(integrations)}")

    # 5. Network connectivity
    try:
        req = urllib.request.urlopen("https://sentry.io/api/0/", timeout=5)
        print(f"[OK]   sentry.io reachable (HTTP {req.status})")
    except Exception as e:
        print(f"[FAIL] sentry.io unreachable: {e}")

    # 6. Service status
    try:
        req = urllib.request.urlopen("https://status.sentry.io/api/v2/status.json", timeout=5)
        data = json.loads(req.read())
        print(f"[INFO] Sentry status: {data['status']['description']}")
    except Exception:
        print("[WARN] Could not fetch Sentry status")

    # 7. Test event
    event_id = sentry_sdk.capture_message("sentry-diagnostics test event", level="info")
    print(f"[INFO] Test event ID: {event_id}")

    # 8. Flush
    sentry_sdk.flush(timeout=10)
    print("[OK]   Flush complete")

if __name__ == "__main__":
    run_diagnostics()
```

## Resources

- [Sentry Troubleshooting Guide (JavaScript)](https://docs.sentry.io/platforms/javascript/troubleshooting/) — official SDK debugging steps
- [Sentry Troubleshooting Guide (Python)](https://docs.sentry.io/platforms/python/troubleshooting/) — Python-specific diagnostics
- [Source Maps Troubleshooting](https://docs.sentry.io/platforms/javascript/sourcemaps/troubleshooting_js/) — `sourcemaps explain` and URL prefix debugging
- [sentry-cli Reference](https://docs.sentry.io/cli/) — CLI installation, auth, `send-event`, `sourcemaps` commands
- [Sentry Status Page](https://status.sentry.io) — real-time platform health
- [Sentry Support](https://sentry.io/support/) — submit tickets with your debug bundle attached
- [sentry-javascript GitHub Issues](https://github.com/getsentry/sentry-javascript/issues) — known bugs and community reports

## Next Steps

After collecting the debug bundle:

1. **Events missing?** Check `beforeSend` hook — add logging to confirm events are not being dropped
2. **Source maps broken?** Run `sentry-cli sourcemaps explain --org ORG --project PROJ EVENT_ID` to diagnose URL prefix mismatches
3. **Performance data missing?** Verify `tracesSampleRate` is non-zero and the instrumentation integration is active
4. **Rate limited?** Review org quotas at Settings > Subscription and reduce sample rates
5. **Need deeper tracing?** Enable `debug: true` in `Sentry.init()` to see full SDK lifecycle in console
6. **Ready to file a ticket?** Attach the generated `sentry-debug-*.md` file to your request at [sentry.io/support](https://sentry.io/support/)
