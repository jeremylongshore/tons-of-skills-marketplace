# Dual-Write Pattern

For mission-critical errors, write to multiple destinations simultaneously. Use `Promise.allSettled` so one destination's failure never blocks the others.

## TypeScript Implementation

```typescript
import * as Sentry from '@sentry/node';

interface ErrorDestination {
  name: string;
  capture: (error: Error, context: Record<string, unknown>) => void | Promise<void>;
}

const destinations: ErrorDestination[] = [
  {
    name: 'sentry',
    capture: (error, context) => {
      Sentry.withScope((scope) => {
        scope.setLevel('fatal');
        scope.setContext('critical', context);
        Sentry.captureException(error);
      });
    },
  },
  {
    name: 'structured-log',
    capture: (error, context) => {
      console.error(JSON.stringify({
        level: 'FATAL',
        error: error.message,
        stack: error.stack,
        context,
        timestamp: new Date().toISOString(),
      }));
    },
  },
  {
    name: 'file-log',
    capture: (error, context) => {
      const fs = require('fs');
      fs.appendFileSync(
        '/var/log/app-errors.log',
        JSON.stringify({
          error: error.message,
          context,
          timestamp: new Date().toISOString(),
        }) + '\n',
      );
    },
  },
];

/** Capture a critical error to all destinations in parallel. */
async function captureCritical(
  error: Error,
  context: Record<string, unknown>,
): Promise<void> {
  const results = await Promise.allSettled(
    destinations.map(async (dest) => {
      try {
        await dest.capture(error, context);
      } catch (e) {
        console.error(`[DualWrite] ${dest.name} failed:`, e);
        throw e;
      }
    }),
  );

  const failed = results
    .map((r, i) => (r.status === 'rejected' ? destinations[i].name : null))
    .filter(Boolean);

  if (failed.length > 0) {
    console.warn(`[DualWrite] Failed destinations: ${failed.join(', ')}`);
  }
}
```

## Python Implementation

```python
import json
import time
import sentry_sdk
from concurrent.futures import ThreadPoolExecutor, as_completed

def capture_critical(error: Exception, context: dict) -> None:
    """Send critical error to all destinations in parallel."""
    def to_sentry():
        with sentry_sdk.push_scope() as scope:
            scope.set_level("fatal")
            scope.set_context("critical", context)
            sentry_sdk.capture_exception(error)

    def to_structured_log():
        print(json.dumps({
            "level": "FATAL",
            "error": str(error),
            "context": context,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }))

    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {
            pool.submit(to_sentry): "sentry",
            pool.submit(to_structured_log): "structured-log",
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"[DualWrite] {name} failed: {e}")
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io)*
