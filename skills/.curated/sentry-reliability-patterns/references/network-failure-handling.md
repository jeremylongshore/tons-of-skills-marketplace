# Network Failure Handling

## Offline Event Queue — TypeScript

```typescript
// lib/sentry-offline-queue.ts
import * as Sentry from '@sentry/node';
import { writeFileSync, readFileSync, existsSync, unlinkSync } from 'fs';

const QUEUE_PATH = process.env.SENTRY_QUEUE_PATH ?? '/tmp/sentry-offline-queue.json';
const MAX_QUEUED_EVENTS = 1000; // cap to prevent unbounded disk growth

interface QueuedEvent {
  timestamp: number;
  error: { name: string; message: string; stack?: string };
  context?: Record<string, unknown>;
  tags?: Record<string, string>;
}

/** Buffer an error event to disk when Sentry is unreachable. */
export function enqueueEvent(
  error: Error,
  context?: Record<string, unknown>,
  tags?: Record<string, string>,
): void {
  try {
    const queue: QueuedEvent[] = existsSync(QUEUE_PATH)
      ? JSON.parse(readFileSync(QUEUE_PATH, 'utf-8'))
      : [];

    queue.push({
      timestamp: Date.now(),
      error: { name: error.name, message: error.message, stack: error.stack },
      context,
      tags,
    });

    // Evict oldest events if over capacity
    if (queue.length > MAX_QUEUED_EVENTS) {
      queue.splice(0, queue.length - MAX_QUEUED_EVENTS);
    }

    writeFileSync(QUEUE_PATH, JSON.stringify(queue, null, 2));
    console.log(`[Sentry Queue] Buffered event (${queue.length} queued)`);
  } catch (writeError) {
    console.error('[Sentry Queue] Failed to write queue file:', writeError);
  }
}

/**
 * Drain all queued events to Sentry.
 * Call on startup, after connectivity restores, or on a periodic timer.
 */
export async function drainQueue(): Promise<number> {
  if (!existsSync(QUEUE_PATH)) return 0;

  let queue: QueuedEvent[];
  try {
    queue = JSON.parse(readFileSync(QUEUE_PATH, 'utf-8'));
  } catch {
    console.error('[Sentry Queue] Corrupt queue file — removing');
    unlinkSync(QUEUE_PATH);
    return 0;
  }

  if (queue.length === 0) return 0;

  console.log(`[Sentry Queue] Draining ${queue.length} queued events`);

  for (const item of queue) {
    Sentry.withScope((scope) => {
      scope.setTag('offline_queued', 'true');
      scope.setTag('queued_at', new Date(item.timestamp).toISOString());
      if (item.tags) {
        for (const [key, value] of Object.entries(item.tags)) {
          scope.setTag(key, value);
        }
      }
      if (item.context) scope.setContext('queued_context', item.context);

      const reconstructed = new Error(item.error.message);
      reconstructed.name = item.error.name;
      reconstructed.stack = item.error.stack;
      Sentry.captureException(reconstructed);
    });
  }

  // Flush with generous timeout — may be sending many events
  const flushed = await Sentry.flush(15_000);
  if (flushed) {
    unlinkSync(QUEUE_PATH);
    console.log(`[Sentry Queue] Successfully drained ${queue.length} events`);
  } else {
    console.warn('[Sentry Queue] Flush timed out — events may not have been delivered');
  }

  return queue.length;
}
```

## Offline Event Queue — Python

```python
import json
import os
import time
from pathlib import Path
from typing import Optional
import sentry_sdk

QUEUE_PATH = os.getenv("SENTRY_QUEUE_PATH", "/tmp/sentry-offline-queue.json")
MAX_QUEUED = 1000

def enqueue_event(error: Exception, context: Optional[dict] = None):
    """Buffer an error event to disk for later replay."""
    try:
        queue = json.loads(Path(QUEUE_PATH).read_text()) if Path(QUEUE_PATH).exists() else []
        queue.append({
            "timestamp": time.time(),
            "error": {"type": type(error).__name__, "message": str(error)},
            "context": context,
        })
        if len(queue) > MAX_QUEUED:
            queue = queue[-MAX_QUEUED:]
        Path(QUEUE_PATH).write_text(json.dumps(queue, indent=2))
    except Exception as e:
        print(f"[Sentry Queue] Write failed: {e}")

def drain_queue() -> int:
    """Replay queued events to Sentry. Returns count of drained events."""
    if not Path(QUEUE_PATH).exists():
        return 0
    try:
        queue = json.loads(Path(QUEUE_PATH).read_text())
    except (json.JSONDecodeError, OSError):
        Path(QUEUE_PATH).unlink(missing_ok=True)
        return 0

    for item in queue:
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("offline_queued", "true")
            scope.set_context("queued", item.get("context", {}))
            sentry_sdk.capture_message(
                f"[Queued] {item['error']['type']}: {item['error']['message']}",
                level="error",
            )

    sentry_sdk.flush(timeout=15)
    Path(QUEUE_PATH).unlink(missing_ok=True)
    return len(queue)
```

## Connectivity Check Pattern

```typescript
// Periodically check if Sentry is reachable and drain queue
class ConnectivityMonitor {
  private intervalId?: ReturnType<typeof setInterval>;

  start(intervalMs = 30_000): void {
    this.intervalId = setInterval(async () => {
      const reachable = await this.checkSentryReachable();
      if (reachable) {
        const { drainQueue } = await import('./sentry-offline-queue');
        const count = await drainQueue();
        if (count > 0) console.log(`[Monitor] Replayed ${count} offline events`);
      }
    }, intervalMs);
  }

  stop(): void {
    if (this.intervalId) clearInterval(this.intervalId);
  }

  private async checkSentryReachable(): Promise<boolean> {
    try {
      const resp = await fetch('https://sentry.io/api/0/', { method: 'HEAD' });
      return resp.ok;
    } catch {
      return false;
    }
  }
}

export const monitor = new ConnectivityMonitor();
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io)*
