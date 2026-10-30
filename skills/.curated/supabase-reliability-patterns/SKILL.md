---
name: supabase-reliability-patterns
description: 'Build resilient Supabase integrations: circuit breakers wrapping database

  calls, offline queue with IndexedDB, graceful degradation with cached fallbacks,

  health check endpoints, retry with exponential backoff and jitter,

  and dual-write patterns for critical data.

  Use when building fault-tolerant apps, handling Supabase outages gracefully,

  implementing offline-first patterns, or adding retry logic to SDK calls.

  Trigger with phrases like "supabase circuit breaker", "supabase offline",

  "supabase retry", "supabase health check", "supabase fallback",

  "supabase resilience", "supabase dual write", "supabase outage".

  '
allowed-tools: Read, Write, Edit, Bash(supabase:*), Bash(curl:*), Grep
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - supabase
  - reliability
  - resilience
  - circuit-breaker
  - offline
  - retry
compatibility: Designed for Claude Code
---

# Supabase Reliability Patterns

## Overview

Use bounded retries for explicitly idempotent reads, and a circuit breaker that
recognizes Supabase database queries' returned `{ data, error }` failures. Do not
retry arbitrary writes, Auth failures, or RLS denials. Browser/session clients must
not be shared across unrelated server requests; use request-scoped SSR clients.

## Prerequisites

- A configured client scoped to the authenticated request or a stateless public read
- Reviewed idempotency and retry budgets for each operation
- Explicit UI treatment of unavailable/stale data; an outage is not an empty dataset

## Instructions

### Step 1: Bound Read Retries

This helper retries only returned error codes in the explicit transient-read set.
`PGRST301` is an invalid/undecodable JWT, not a connection failure. Auth, RLS, schema,
and validation errors are not retried. A thrown transport exception propagates to
the caller; deciding whether it is safe to retry requires an operation-specific
policy. `maxRetries` means additional attempts after the first, capped here at five.

```typescript
export type QueryResult<T> = {
  data: T | null;
  error: { code?: string; message?: string } | null;
};
export type RetryOptions = { maxRetries: number; baseDelayMs: number; maxDelayMs: number };
const TRANSIENT_READ_CODES = new Set(['08006', '53300', 'PGRST001', 'PGRST002', 'PGRST003']);

export async function withReadRetry<T>(
  fn: () => Promise<QueryResult<T>>,
  opts: RetryOptions = { maxRetries: 3, baseDelayMs: 200, maxDelayMs: 5000 },
  sleep: (ms: number) => Promise<void> = (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
  random: () => number = Math.random,
): Promise<QueryResult<T>> {
  if (
    !Number.isInteger(opts.maxRetries) ||
    opts.maxRetries < 0 ||
    opts.maxRetries > 5 ||
    !Number.isFinite(opts.baseDelayMs) ||
    opts.baseDelayMs < 0 ||
    !Number.isFinite(opts.maxDelayMs) ||
    opts.maxDelayMs < opts.baseDelayMs
  ) {
    throw new Error('Invalid retry budget');
  }
  for (let attempt = 0; ; attempt++) {
    const result = await fn();
    if (
      !result.error ||
      !TRANSIENT_READ_CODES.has(result.error.code ?? '') ||
      attempt >= opts.maxRetries
    )
      return result;
    const jitter = random();
    if (!Number.isFinite(jitter) || jitter < 0 || jitter > 1) throw new Error('Invalid jitter');
    await sleep(Math.min(opts.maxDelayMs, opts.baseDelayMs * 2 ** attempt) * jitter);
  }
}
```

A deadline/abort policy is still required for each query and the whole request;
finite attempts do not bound a stalled network call. The injectable sleep/random
functions permit local deterministic tests without waiting or provider requests.

### Step 2: Count Returned Errors in a Circuit Breaker

This single-process illustrative circuit throws a generic error for failed database
results, so a returned SDK error cannot be counted as success. Only exhausted
transient failures open it; nonretryable Auth/RLS failures propagate without being
presented as an outage. One half-open probe runs at a time. This is not a distributed
admission controller or a substitute for request cancellation. Generation and
probe ownership fence older in-flight completions from changing a newer circuit
state or releasing its half-open probe.

```typescript
export class ReadCircuit {
  private failures = 0;
  private openedAt: number | null = null;
  private generation = 0;
  private probe: object | null = null;
  constructor(
    private threshold = 3,
    private resetMs = 30_000,
    private now: () => number = Date.now,
  ) {
    if (!Number.isInteger(threshold) || threshold < 1 || !Number.isFinite(resetMs) || resetMs < 0) {
      throw new Error('Invalid circuit budget');
    }
  }
  async call<T>(fn: () => Promise<QueryResult<T>>): Promise<T | null> {
    const generation = this.generation;
    const wasOpen = this.openedAt !== null;
    let ownedProbe: object | null = null;
    if (wasOpen) {
      if (this.now() - this.openedAt! < this.resetMs || this.probe !== null) {
        throw new Error('Circuit open');
      }
      ownedProbe = {};
      this.probe = ownedProbe;
    }
    const ownsState = () =>
      this.generation === generation && (!wasOpen || this.probe === ownedProbe);
    try {
      const result = await fn();
      if (result.error) {
        if (ownsState()) {
          if (TRANSIENT_READ_CODES.has(result.error.code ?? '')) {
            this.failures++;
            if (wasOpen || this.failures >= this.threshold) {
              this.openedAt = this.now();
              this.generation++;
            }
          } else if (wasOpen) {
            // Service responded, but this operation was denied/invalid.
            this.openedAt = null;
            this.failures = 0;
            this.generation++;
          }
        }
        throw new Error('Database read failed');
      }
      if (ownsState()) {
        this.failures = 0;
        this.openedAt = null;
        if (wasOpen) this.generation++;
      }
      return result.data;
    } catch (error) {
      if (wasOpen && ownsState() && this.openedAt !== null) {
        this.openedAt = this.now();
        this.generation++;
      }
      throw error;
    } finally {
      // A stale closed request cannot release another request's half-open probe.
      if (ownedProbe !== null && this.probe === ownedProbe) this.probe = null;
    }
  }
}
```

Thrown transport exceptions propagate; this example deliberately does not classify
every exception as a transient outage. A failed half-open transport probe leaves the
circuit open, and the next caller must still respect the reset budget.

### Step 3: Compose Only an Authorized Read

```typescript
import type { SupabaseClient } from '@supabase/supabase-js';
// Import the helpers above from your application's reliability module.

export async function listOwnTodos(client: SupabaseClient, circuit: ReadCircuit) {
  const {
    data: { user },
    error,
  } = await client.auth.getUser();
  if (error || !user) throw new Error('Verified user required');
  return circuit.call(() =>
    withReadRetry(
      async () =>
        await client
          .from('todos')
          .select('id, title, is_complete')
          .eq('user_id', user.id)
          .order('id')
          .limit(100),
    ),
  );
}
```

The existing table needs matching RLS. Do not share cached results across identities.
Do not wrap `.insert()` in this read-retry helper: a timeout can follow a committed
write. A write queue needs durable operation IDs, authorization on replay, bounded
retention, reconciliation and application-owned idempotency before retries.

## Output

- Explicit attempt limits and nonretryable errors returned on the first failure
- Returned SDK failures counted by the read circuit rather than mistaken for success
- Unavailable data distinguished from a genuinely empty successful result
- Separate reviewed write-replay, cache, deadline, and recovery policies

## Error Handling

| Failure                  | Disposition                                                  |
| ------------------------ | ------------------------------------------------------------ |
| PGRST301 / auth / RLS    | Correct identity/policy; no blind retry                      |
| Exhausted transient read | Surface unavailable; circuit may open                        |
| Circuit open             | No provider query; return an explicit unavailable state      |
| Write timeout            | Reconcile operation ID before deciding whether to repeat     |
| Stale cache              | Label age/scope; never pretend it is a fresh successful read |

## Examples

Test first-attempt success, zero retries, nonretryable first failure, exact exhaustion,
transient recovery, thrown exceptions, returned-error opening, and half-open recovery
with injected clock/sleep. Test cross-user isolation separately.

Additional patterns in [offline recovery guidance](references/offline-degradation-health-dualwrite.md)
need their own durability and replay review; illustrative dual writes alone cannot
guarantee that critical data survives an outage or that effects happen exactly once.

## Resources

- [PostgREST errors](https://docs.postgrest.org/en/stable/references/errors.html)
- [JavaScript queries](https://supabase.com/docs/reference/javascript/select)
- [Supabase status](https://status.supabase.com)

## Next Steps

Document operation-specific deadlines, recovery ownership, and safe write semantics
before applying retries to additional surfaces.
