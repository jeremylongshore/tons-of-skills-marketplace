# Circuit Breaker Pattern

## TypeScript Implementation

```typescript
// lib/sentry-circuit-breaker.ts
import * as Sentry from '@sentry/node';

type CircuitState = 'closed' | 'open' | 'half-open';

interface CircuitBreakerOptions {
  maxFailures: number;     // Failures before tripping open
  resetTimeMs: number;     // Cooldown before half-open probe
  onStateChange?: (from: CircuitState, to: CircuitState) => void;
}

const DEFAULT_OPTIONS: CircuitBreakerOptions = {
  maxFailures: 5,
  resetTimeMs: 60_000, // 1 minute cooldown
};

class SentryCircuitBreaker {
  private failures = 0;
  private lastFailureAt = 0;
  private state: CircuitState = 'closed';
  private opts: CircuitBreakerOptions;

  constructor(options: Partial<CircuitBreakerOptions> = {}) {
    this.opts = { ...DEFAULT_OPTIONS, ...options };
  }

  /**
   * Capture an exception through the circuit breaker.
   * Returns Sentry event ID if sent, undefined if circuit is open.
   */
  captureException(
    error: Error,
    context?: Record<string, unknown>,
  ): string | undefined {
    // OPEN: reject immediately until cooldown expires
    if (this.state === 'open') {
      if (Date.now() - this.lastFailureAt > this.opts.resetTimeMs) {
        this.transition('half-open');
      } else {
        console.error('[Sentry Circuit OPEN] Skipping capture:', error.message);
        this.logFallback(error, context);
        return undefined;
      }
    }

    // CLOSED or HALF-OPEN: attempt to send
    try {
      let eventId: string | undefined;
      Sentry.withScope((scope) => {
        if (context) scope.setContext('app', context);
        scope.setTag('circuit_state', this.state);
        eventId = Sentry.captureException(error);
      });

      // Success — if probing (half-open), reset everything
      if (this.state === 'half-open') {
        this.transition('closed');
        this.failures = 0;
      }

      return eventId;
    } catch (sentryError) {
      this.recordFailure();
      this.logFallback(error, context);
      return undefined;
    }
  }

  private recordFailure(): void {
    this.failures++;
    this.lastFailureAt = Date.now();

    if (this.failures >= this.opts.maxFailures) {
      this.transition('open');
      console.error(
        `[Sentry Circuit] OPEN after ${this.failures} failures — ` +
        `pausing for ${this.opts.resetTimeMs / 1000}s`,
      );
    }
  }

  private transition(to: CircuitState): void {
    const from = this.state;
    this.state = to;
    this.opts.onStateChange?.(from, to);
    console.log(`[Sentry Circuit] ${from} → ${to}`);
  }

  private logFallback(error: Error, context?: Record<string, unknown>): void {
    console.error('[Fallback]', JSON.stringify({
      timestamp: new Date().toISOString(),
      error: { name: error.name, message: error.message },
      context,
    }));
  }

  /** Expose state for health check endpoints. */
  getStatus(): { state: CircuitState; failures: number; lastFailureAt: number } {
    return { state: this.state, failures: this.failures, lastFailureAt: this.lastFailureAt };
  }

  /** Manually reset the breaker (admin endpoints or tests). */
  reset(): void {
    this.transition('closed');
    this.failures = 0;
    this.lastFailureAt = 0;
  }
}

export const sentryBreaker = new SentryCircuitBreaker({
  maxFailures: 5,
  resetTimeMs: 60_000,
  onStateChange: (from, to) => {
    console.warn(`[Alert] Sentry circuit breaker: ${from} → ${to}`);
  },
});
```

## Python Implementation

```python
import time
import json
import sentry_sdk
from enum import Enum
from typing import Optional

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half-open"

class SentryCircuitBreaker:
    def __init__(self, max_failures: int = 5, reset_time_s: float = 60.0):
        self.max_failures = max_failures
        self.reset_time_s = reset_time_s
        self.failures = 0
        self.last_failure_at = 0.0
        self.state = CircuitState.CLOSED

    def capture_exception(
        self,
        error: Exception,
        context: Optional[dict] = None,
    ) -> Optional[str]:
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_at > self.reset_time_s:
                self._transition(CircuitState.HALF_OPEN)
            else:
                print(f"[Sentry Circuit OPEN] Skipping: {error}")
                self._log_fallback(error, context)
                return None

        try:
            with sentry_sdk.push_scope() as scope:
                if context:
                    scope.set_context("app", context)
                scope.set_tag("circuit_state", self.state.value)
                event_id = sentry_sdk.capture_exception(error)

            if self.state == CircuitState.HALF_OPEN:
                self._transition(CircuitState.CLOSED)
                self.failures = 0

            return event_id
        except Exception:
            self._record_failure()
            self._log_fallback(error, context)
            return None

    def _record_failure(self):
        self.failures += 1
        self.last_failure_at = time.time()
        if self.failures >= self.max_failures:
            self._transition(CircuitState.OPEN)

    def _transition(self, to: CircuitState):
        print(f"[Sentry Circuit] {self.state.value} → {to.value}")
        self.state = to

    def _log_fallback(self, error: Exception, context: Optional[dict]):
        print(json.dumps({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "error": str(error),
            "context": context,
        }))

    def get_status(self) -> dict:
        return {"state": self.state.value, "failures": self.failures}

breaker = SentryCircuitBreaker()
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io)*
