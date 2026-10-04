---
name: sentry-hello-world
description: 'Capture your first test error with Sentry and verify it appears in the
  dashboard.

  Use when testing a new Sentry integration, verifying error capture works after

  install-auth, or learning how to enrich events with user context, tags, and breadcrumbs.

  Trigger with phrases like "test sentry", "sentry hello world",

  "verify sentry", "first sentry error", "sentry capture test".

  '
allowed-tools: Read, Write, Edit, Bash(node:*), Bash(python:*), Bash(npm:*), Grep
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- testing
- dashboard
- quickstart
compatibility: Designed for Claude Code
---
# Sentry Hello World

## Overview

Send your first test events to Sentry — a captured message, a captured exception, and a fully-enriched error with user context, tags, and breadcrumbs — then verify each one appears in the Sentry dashboard. This skill covers both Node.js (`@sentry/node`) and Python (`sentry-sdk`).

## Prerequisites

- Completed `sentry-install-auth` setup (SDK installed, DSN configured)
- Valid `SENTRY_DSN` in environment variables
- `instrument.mjs` loaded before app code (Node.js) or `sentry_sdk.init()` called (Python)
- Network access to `*.ingest.sentry.io`

## Instructions

### Step 1 — Verify the SDK Is Active

Before sending test events, confirm the SDK initialized correctly. If `getClient()` returns `undefined`, the SDK was never initialized — go back to `sentry-install-auth`.

**TypeScript (Node.js):**

```typescript
import * as Sentry from '@sentry/node';

const client = Sentry.getClient();
if (!client) {
  console.error('Sentry SDK not initialized. Ensure instrument.mjs is loaded first.');
  console.error('Run with: node --import ./instrument.mjs your-script.mjs');
  process.exit(1);
}
console.log('Sentry SDK active — DSN configured');
```

**Python:**

```python
import sentry_sdk

client = sentry_sdk.Hub.current.client
if client is None or client.dsn is None:
    print("Sentry SDK not initialized. Call sentry_sdk.init() first.")
    exit(1)
print("Sentry SDK active — DSN configured")
```

### Step 2 — Capture a Test Message

`captureMessage` sends an informational event without a stack trace. Use it to verify basic connectivity between your app and Sentry.

**TypeScript:**

```typescript
import * as Sentry from '@sentry/node';

// captureMessage returns the event ID (a 32-char hex string)
const eventId = Sentry.captureMessage('Hello Sentry! SDK verification test.', 'info');
console.log(`Message sent — Event ID: ${eventId}`);

// Also test 'warning' level — appears with yellow indicator in dashboard
Sentry.captureMessage('Warning-level test message', 'warning');

// IMPORTANT: flush before process exits or events may be lost
await Sentry.flush(2000);
```

**Python:**

```python
import sentry_sdk

event_id = sentry_sdk.capture_message("Hello Sentry! SDK verification test.", level="info")
print(f"Message sent — Event ID: {event_id}")

sentry_sdk.capture_message("Warning-level test message", level="warning")

# Flush to ensure delivery before process exits
sentry_sdk.flush()
```

### Step 3 — Capture a Test Exception

`captureException` sends a full error with stack trace. Always pass an actual `Error` object (not a string) so Sentry generates a proper stack trace.

**TypeScript:**

```typescript
import * as Sentry from '@sentry/node';

try {
  throw new Error('Hello Sentry! This is a test exception.');
} catch (error) {
  const eventId = Sentry.captureException(error);
  console.log(`Exception sent — Event ID: ${eventId}`);
}

await Sentry.flush(2000);
```

**Python:**

```python
import sentry_sdk

try:
    raise ValueError("Hello Sentry! This is a test exception.")
except Exception as e:
    event_id = sentry_sdk.capture_exception(e)
    print(f"Exception sent — Event ID: {event_id}")

sentry_sdk.flush()
```

### Step 4 — Add User Context and Tags

Enrich events with identity and metadata so you can filter and search in the dashboard. `setUser` attaches to all subsequent events in the current scope. `setTag` creates indexed, searchable key-value pairs.

**TypeScript:**

```typescript
import * as Sentry from '@sentry/node';

// Attach user identity — appears in the "User" section of every event
Sentry.setUser({
  id: 'test-user-001',
  email: 'dev@example.com',
  username: 'developer',
});

// Tags are indexed and searchable — use for filtering in Issues view
Sentry.setTag('test_run', 'hello-world');
Sentry.setTag('team', 'platform');

// setContext adds structured data (not indexed, but visible in event detail)
Sentry.setContext('test_metadata', {
  ran_at: new Date().toISOString(),
  node_version: process.version,
  purpose: 'SDK verification',
});

// This event will carry user, tags, and context
Sentry.captureMessage('Test event with full context attached', 'info');

await Sentry.flush(2000);
```

**Python:**

```python
import sentry_sdk
from datetime import datetime, timezone
import sys

sentry_sdk.set_user({"id": "test-user-001", "email": "dev@example.com", "username": "developer"})

sentry_sdk.set_tag("test_run", "hello-world")
sentry_sdk.set_tag("team", "platform")

sentry_sdk.set_context("test_metadata", {
    "ran_at": datetime.now(timezone.utc).isoformat(),
    "python_version": sys.version,
    "purpose": "SDK verification",
})

sentry_sdk.capture_message("Test event with full context attached", level="info")

sentry_sdk.flush()
```

### Step 5 — Add Breadcrumbs

Breadcrumbs record a trail of events leading up to an error. They appear in the event detail view, giving you the chronological context of what happened before the crash.

**TypeScript:**

```typescript
import * as Sentry from '@sentry/node';

Sentry.addBreadcrumb({
  category: 'auth',
  message: 'User authenticated successfully',
  level: 'info',
});

Sentry.addBreadcrumb({
  category: 'http',
  message: 'GET /api/users returned 200',
  level: 'info',
  data: { status_code: 200, url: '/api/users', method: 'GET' },
});

Sentry.addBreadcrumb({
  category: 'ui',
  message: 'User clicked "Submit Order" button',
  level: 'info',
});

// This exception will carry all three breadcrumbs above
try {
  throw new Error('Order processing failed — breadcrumb trail attached');
} catch (error) {
  Sentry.captureException(error);
}

await Sentry.flush(2000);
```

**Python:**

```python
import sentry_sdk

sentry_sdk.add_breadcrumb(category="auth", message="User authenticated successfully", level="info")
sentry_sdk.add_breadcrumb(category="http", message="GET /api/users returned 200", level="info",
                          data={"status_code": 200, "url": "/api/users"})
sentry_sdk.add_breadcrumb(category="ui", message="User clicked Submit Order button", level="info")

try:
    raise RuntimeError("Order processing failed — breadcrumb trail attached")
except Exception as e:
    sentry_sdk.capture_exception(e)

sentry_sdk.flush()
```

### Step 6 — Verify in the Sentry Dashboard

1. Open **https://sentry.io** and select your project
2. Navigate to the **Issues** tab — test errors appear as grouped issues
3. Click an issue to inspect the event detail:
   - **Stack Trace** — file path, line number, and surrounding code context
   - **User** section — `id`, `email`, `username` from `setUser()`
   - **Tags** sidebar — `test_run: hello-world`, `team: platform`
   - **Breadcrumbs** tab — chronological trail of events before the error
   - **Additional Data** — custom context from `setContext()`
4. Use the search bar to filter: `test_run:hello-world` narrows to your test events
5. Confirm **Environment** matches your `SENTRY_ENVIRONMENT` value
6. Confirm **Release** matches your `SENTRY_RELEASE` value (if set)
7. Delete test issues when done: select issues > **Resolve** or **Delete**

## Examples

### Complete Verification Script (TypeScript)

Save as `test-sentry.mjs` and run with `node --import ./instrument.mjs test-sentry.mjs` to exercise all capabilities at once.

```typescript
// Run with: node --import ./instrument.mjs test-sentry.mjs
import * as Sentry from '@sentry/node';

async function main() {
  console.log('--- Sentry Hello World Verification ---\n');

  // 1. Verify SDK
  const client = Sentry.getClient();
  if (!client) {
    console.error('ERROR: Sentry SDK not initialized.');
    console.error('Run with: node --import ./instrument.mjs test-sentry.mjs');
    process.exit(1);
  }
  console.log('[OK] Sentry SDK active');

  // 2. Set user context and tags
  Sentry.setUser({ id: 'test-001', email: 'dev@example.com', username: 'developer' });
  Sentry.setTag('test_run', 'hello-world');
  Sentry.setTag('environment', process.env.SENTRY_ENVIRONMENT || 'test');
  console.log('[OK] User context and tags set');

  // 3. Capture a message
  const msgId = Sentry.captureMessage('Hello Sentry — SDK verification', 'info');
  console.log(`[OK] Message captured — Event ID: ${msgId}`);

  // 4. Capture an exception with breadcrumbs
  Sentry.addBreadcrumb({ category: 'test', message: 'Starting verification script', level: 'info' });
  Sentry.addBreadcrumb({ category: 'test', message: 'About to throw test error', level: 'warning' });

  try {
    throw new Error('Hello Sentry! Verification test exception.');
  } catch (error) {
    const errId = Sentry.captureException(error);
    console.log(`[OK] Exception captured — Event ID: ${errId}`);
  }

  // 5. Flush and report
  await Sentry.flush(5000);
  console.log('\n[DONE] All events flushed — check your Sentry dashboard at https://sentry.io');
  console.log('Navigate to Issues tab, filter by tag: test_run:hello-world');
}

main();
```

### Complete Verification Script (Python)

Save as `test_sentry.py` and run with `python test_sentry.py` (after calling `sentry_sdk.init()` in your setup).

```python
# Run with: python test_sentry.py (after sentry_sdk.init() in your setup)
import sentry_sdk
import os
import sys

def main():
    print("--- Sentry Hello World Verification ---\n")

    # 1. Verify SDK
    client = sentry_sdk.Hub.current.client
    if client is None or client.dsn is None:
        print("ERROR: Sentry SDK not initialized.")
        print("Ensure sentry_sdk.init(dsn=...) is called before this script.")
        sys.exit(1)
    print("[OK] Sentry SDK active")

    # 2. Set user context and tags
    sentry_sdk.set_user({"id": "test-001", "email": "dev@example.com", "username": "developer"})
    sentry_sdk.set_tag("test_run", "hello-world")
    sentry_sdk.set_tag("environment", os.environ.get("SENTRY_ENVIRONMENT", "test"))
    print("[OK] User context and tags set")

    # 3. Capture a message
    msg_id = sentry_sdk.capture_message("Hello Sentry — SDK verification", level="info")
    print(f"[OK] Message captured — Event ID: {msg_id}")

    # 4. Capture an exception with breadcrumbs
    sentry_sdk.add_breadcrumb(category="test", message="Starting verification script", level="info")
    sentry_sdk.add_breadcrumb(category="test", message="About to throw test error", level="warning")

    try:
        raise ValueError("Hello Sentry! Verification test exception.")
    except Exception as e:
        err_id = sentry_sdk.capture_exception(e)
        print(f"[OK] Exception captured — Event ID: {err_id}")

    # 5. Flush and report
    sentry_sdk.flush()
    print("\n[DONE] All events flushed — check your Sentry dashboard at https://sentry.io")
    print("Navigate to Issues tab, filter by tag: test_run:hello-world")

if __name__ == "__main__":
    main()
```

## Output

- Test message visible in Sentry dashboard Issues tab within 30 seconds
- Test exception visible with full stack trace pointing to correct file and line
- User context (`id`, `email`, `username`) attached to every event
- Tags (`test_run`, `team`) searchable in the Issues sidebar filter
- Breadcrumb trail visible in event detail, showing events leading up to the error
- Custom context visible under "Additional Data" in event detail
- Event IDs printed to console for cross-referencing with dashboard

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Event not appearing in dashboard | DSN misconfigured or env var not loaded | Run `echo $SENTRY_DSN` to verify; re-copy from Project Settings > Client Keys |
| `getClient()` returns `undefined` | SDK not initialized before test code runs | Use `node --import ./instrument.mjs` flag or import instrument at top of entry |
| Missing stack trace on exception | Error captured as string instead of Error object | Always pass `new Error('...')` to `captureException`, never a bare string |
| No user context on event | `setUser()` called after `captureException()` | Call `setUser()` before any capture calls |
| Events delayed > 60 seconds | Network or proxy blocking `*.ingest.sentry.io` | Check firewall rules; test with `curl https://sentry.io/api/0/` |
| `Sentry Logger [warn]: Too many requests` | Rate limited by Sentry ingest | Lower `tracesSampleRate` in init; check quota at Settings > Subscription |
| `flush()` times out | Large event queue or slow network | Increase timeout: `Sentry.flush(10000)`; check network latency |
| Breadcrumbs not appearing | Max breadcrumbs exceeded (default 100) | Configure `maxBreadcrumbs` in `Sentry.init()` or clear with `Sentry.getCurrentScope().clearBreadcrumbs()` |

## Resources

- [Capturing Errors — Node.js](https://docs.sentry.io/platforms/javascript/guides/node/usage/)
- [Capturing Errors — Python](https://docs.sentry.io/platforms/python/usage/)
- [Enriching Events — Context, Tags, User](https://docs.sentry.io/platforms/javascript/enriching-events/)
- [Breadcrumbs Guide](https://docs.sentry.io/platforms/javascript/enriching-events/breadcrumbs/)
- [Sentry Issue Search Syntax](https://docs.sentry.io/concepts/search/)

## Next Steps

Proceed to `sentry-error-capture` for production error-handling patterns with scope isolation, custom fingerprinting, and error grouping strategies.
