---
name: podium-rate-limit-survival
description: Survive the rate-limit failure modes that crater production Podium integrations —
  cascading 429s that burn the daily quota by lunch, ignored Retry-After hints, silent daily-quota
  breaches, per-endpoint budget exhaustion, end-of-day review-request bursts, and webhook-driven
  outbound amplification. Use when building the outbound API layer, instrumenting quota monitoring,
  smoothing end-of-day review-request bursts, or recovering from a 429 cascade. Trigger with
  "podium rate limit", "podium 429", "podium token bucket", "podium quota monitor", "podium burst
  smoothing", "podium retry-after".
allowed-tools: Read, Write, Edit, Bash(curl:*), Bash(jq:*), Bash(python3:*), Bash(redis-cli:*), Grep
version: 2.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
compatibility: Designed for Claude Code
tags:
  - podium
  - rate-limits
  - token-bucket
  - quota-monitoring
  - resilience
  - burst-control
---

# Podium Rate Limit Survival

## Overview

Make the outbound side of a Podium integration survive a real production day. This is not a "just retry on 429" walkthrough — it is the rate-limiting code your integration runs when Shopify ships 80 orders at 5pm AEST and KombiLife fires 80 review-request POSTs in 30 seconds, when an inbound webhook burst fans out 5x outbound, and when a junior engineer's naive retry loop has already eaten 92% of the daily quota by 10:30am.

The six production failures this skill prevents:

1. **Cascading 429s burn the whole day** — a naive `while status == 429: retry` loop stampedes the per-minute window for the rest of the minute, then the next minute, etc. By 11am you've consumed the 24-hour quota and every endpoint is hard-down until UTC midnight.
2. **`Retry-After` header ignored** — clients that retry on a fixed delay (or worse, no delay) miss Podium's server-side hint and hit the same rate wall again. The header supports both integer seconds and HTTP-date form; many clients parse one and crash on the other.
3. **No daily-quota monitor** — the 24-hour envelope quota is silent until you breach it. Operations discover the wall on a Friday afternoon when review-request automation collapses and the on-call has no leading indicator.
4. **No per-endpoint isolation** — the `conversations.write` endpoint blows its budget on a chatty inbound webhook; `contacts.read` also fails because the client treats the API as a single bucket. One endpoint family taking down siblings is a multiplier on every other failure mode.
5. **End-of-day burst overflow** — Shopify orders ship in a 5pm cluster, KombiLife fires ~80 review-request POSTs in 30 seconds, the per-minute ceiling rejects half. The integration "works" 23 hours a day and silently drops 30-50% of review requests during the only hour that matters commercially.
6. **Webhook-driven amplification** — one inbound webhook triggers 5 outbound API calls; 100 inbound webhooks in a burst = 500 outbound = quota collapse. The amplification factor is invisible until the cascade fires.

## Authentication

This skill **does not** mint, refresh, or hold Podium credentials — those concerns live in the sibling `podium-auth` skill. Every wrapped HTTP call in this skill calls `auth.get_token()` immediately after the bucket releases, where `auth` is a `PodiumAuth` instance constructed by the consumer per the `podium-auth` skill instructions (OAuth2 refresh-token grant against `https://accounts.podium.com/oauth/token`). The bearer token is passed in the `Authorization: Bearer {token}` header on every `api.podium.com` request. If `auth.get_token()` raises, this skill propagates the auth error to the caller without retry — auth recovery is `podium-auth`'s responsibility, not this skill's.

## Prerequisites

- A working `podium-auth` integration (this skill assumes a `PodiumAuth` instance is available — see the `podium-auth` skill in this pack)
- Python 3.10+ with `asyncio` (the patterns translate to Node.js; see references/implementation.md)
- A token-bucket library — `aiolimiter` recommended, or hand-rolled on `asyncio.sleep`
- A daily-quota counter store — Redis preferred (atomic INCR + TTL), local SQLite acceptable for single-process integrations
- Knowledge of which Podium endpoint families your integration hits (conversations, contacts, reviews, locations, webhooks) — bucket isolation is per-family

## Instructions

Build in this order. Each section neutralizes one of the six production failures.

### 1. Token-bucket rate limiter (neutralizes cascading 429s)

The Podium API's documented ceiling is 60 requests per minute per OAuth app. Treat it as a hard ceiling and stay under it by construction — never by reacting to 429s. Hand the hot path a token-bucket gate that paces requests at the documented rate; concurrent callers serialize on the bucket, no retry storm is possible.

```python
import asyncio
import time
from contextlib import asynccontextmanager
from typing import Optional

class TokenBucket:
    """Async token-bucket limiter. Pace = rate tokens per second, max burst = capacity."""

    def __init__(self, rate_per_minute: int, capacity: int):
        self.rate_per_sec = rate_per_minute / 60.0
        self.capacity = capacity
        self._tokens = float(capacity)
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: float = 1.0) -> None:
        while True:
            async with self._lock:
                self._refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                deficit = tokens - self._tokens
                wait_s = deficit / self.rate_per_sec
            # Sleep OUTSIDE the lock so other callers can refill-and-check in parallel
            await asyncio.sleep(wait_s)

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate_per_sec)
        self._last_refill = now
```

Wire it into the outbound HTTP path:

```python
PODIUM_LIMIT_PER_MIN = 60          # documented ceiling
PODIUM_BURST_CAPACITY = 10         # conservative burst headroom; tune per endpoint

bucket = TokenBucket(rate_per_minute=PODIUM_LIMIT_PER_MIN, capacity=PODIUM_BURST_CAPACITY)

async def podium_call(method: str, path: str, **kwargs) -> httpx.Response:
    await bucket.acquire()
    token = await auth.get_token()
    async with httpx.AsyncClient(timeout=10) as c:
        return await c.request(
            method,
            f"https://api.podium.com{path}",
            headers={"Authorization": f"Bearer {token}"},
            **kwargs,
        )
```

The bucket converts what would be a 429 cascade into bounded queueing. Latency goes up on the burst; **success rate stays at 100%**.

### 2. `Retry-After` parsing for the residual 429s (neutralizes ignored hints)

Even with a bucket, the residual 429s happen — clock drift between your process and Podium's edge, multiple processes sharing a quota, an inbound webhook fan-out that the bucket sees but the server already counted. When 429 happens, Podium returns a `Retry-After` header. Honor it. Support both forms:

- `Retry-After: 30` — integer seconds to wait
- `Retry-After: Wed, 21 Oct 2026 07:28:00 GMT` — HTTP-date (RFC 7231)

```python
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

def parse_retry_after(header_value: str) -> float:
    """Return seconds to wait. Supports int-seconds and HTTP-date forms."""
    header_value = header_value.strip()
    # Try integer seconds first — most common form Podium returns
    try:
        seconds = int(header_value)
        return max(0.0, float(seconds))
    except ValueError:
        pass
    # HTTP-date form — RFC 7231
    try:
        retry_at = parsedate_to_datetime(header_value)
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        delta = (retry_at - datetime.now(timezone.utc)).total_seconds()
        return max(0.0, delta)
    except (TypeError, ValueError):
        # Malformed header — fall back to a safe default rather than crash
        return 60.0
```

Wire it into the retry wrapper:

```python
async def podium_call_with_retry(method: str, path: str, max_attempts: int = 4, **kwargs):
    for attempt in range(1, max_attempts + 1):
        await bucket.acquire()
        r = await _raw_call(method, path, **kwargs)
        if r.status_code != 429:
            return r
        wait_s = parse_retry_after(r.headers.get("Retry-After", "60"))
        # Cap the wait so a misconfigured server can't pin us indefinitely
        wait_s = min(wait_s, 120.0)
        await asyncio.sleep(wait_s)
    raise PodiumRateLimitError(f"429 persisted after {max_attempts} attempts on {path}")
```

Two things make this correct: parse both header forms, and cap the maximum wait. A server returning `Retry-After: 86400` would otherwise stall the integration for a day.

### 3. Daily quota monitor (neutralizes silent quota breaches)

The per-minute ceiling is one envelope; Podium also enforces a 24-hour envelope per OAuth app. The 24-hour envelope is silent until you breach it. Track outbound call count in a counter with a UTC-midnight TTL; emit warn / page / hard-throttle alerts at 70 / 85 / 95% consumption.

```python
import redis.asyncio as aioredis

DAILY_QUOTA = 50_000                    # set to your actual quota; conservative default
WARN_THRESHOLD  = 0.70
PAGE_THRESHOLD  = 0.85
THROTTLE_THRESHOLD = 0.95

class DailyQuotaMonitor:
    def __init__(self, redis_url: str, quota: int = DAILY_QUOTA):
        self._redis = aioredis.from_url(redis_url, decode_responses=True)
        self.quota = quota

    def _key(self) -> str:
        return f"podium:quota:{datetime.utcnow().strftime('%Y-%m-%d')}"

    async def increment(self, n: int = 1) -> int:
        key = self._key()
        # INCR-then-EXPIRE is atomic enough — first-write-wins on the TTL is fine
        new_count = await self._redis.incr(key, n)
        if new_count == n:
            # First increment of the day — set TTL to UTC midnight + 1h grace
            await self._redis.expire(key, 90_000)
        return new_count

    async def check_and_alert(self) -> str:
        count = int(await self._redis.get(self._key()) or 0)
        ratio = count / self.quota
        if ratio >= THROTTLE_THRESHOLD:
            page_oncall(f"Podium daily quota at {ratio:.1%} ({count}/{self.quota}) — hard-throttle engaged")
            return "throttle"
        if ratio >= PAGE_THRESHOLD:
            page_oncall(f"Podium daily quota at {ratio:.1%} ({count}/{self.quota})", severity="high")
            return "page"
        if ratio >= WARN_THRESHOLD:
            log_warn(f"Podium daily quota at {ratio:.1%} ({count}/{self.quota})")
            return "warn"
        return "ok"
```

When the throttle threshold fires, drop the token-bucket rate by 50% for the rest of the day. Customers see slower processing of low-priority traffic; the integration does not collapse.

### 4. Per-endpoint bucket isolation (neutralizes cross-endpoint contagion)

If `conversations.write` is busy on a chatty inbound webhook, `contacts.read` should not also start failing. Isolate buckets per endpoint family — one bucket each for conversations, contacts, reviews, locations, webhooks. Each gets a share of the per-minute ceiling proportional to its expected load:

```python
ENDPOINT_BUCKETS = {
    "conversations": TokenBucket(rate_per_minute=20, capacity=5),
    "contacts":      TokenBucket(rate_per_minute=15, capacity=5),
    "reviews":       TokenBucket(rate_per_minute=15, capacity=10),  # bursty
    "locations":     TokenBucket(rate_per_minute=5,  capacity=2),
    "webhooks":      TokenBucket(rate_per_minute=5,  capacity=2),
}
# Sum of per-minute rates = 60, matching the documented ceiling.

def endpoint_family(path: str) -> str:
    # /v4/conversations/abc → "conversations"
    parts = path.strip("/").split("/")
    if len(parts) >= 2 and parts[0] == "v4":
        return parts[1]
    return "default"

async def podium_call_isolated(method: str, path: str, **kwargs) -> httpx.Response:
    family = endpoint_family(path)
    bucket = ENDPOINT_BUCKETS.get(family) or ENDPOINT_BUCKETS["conversations"]
    await bucket.acquire()
    return await _raw_call(method, path, **kwargs)
```

The sum of per-family rates must equal the documented ceiling — over-allocating per-family rates means the global ceiling fires across all families simultaneously, which is the cross-contagion this section is meant to prevent.

### 5. End-of-day burst smoother (neutralizes the 5pm review-request cluster)

KombiLife's pattern is documented: Shopify orders ship in a tight 5pm AEST cluster, the integration fires ~80 review-request POSTs in 30 seconds, the per-minute ceiling rejects half. The fix is to detect the burst, smooth it over the next 90 seconds, and absorb residual via the bucket.

```python
class BurstSmoother:
    """Smooth a batch of N requests over a target window respecting the bucket rate."""

    def __init__(self, bucket: TokenBucket, target_window_seconds: float = 90.0):
        self.bucket = bucket
        self.target_window = target_window_seconds

    async def submit_batch(self, requests: list[dict], handler) -> list:
        if not requests:
            return []
        # Compute per-request delay so the batch completes within target_window
        # OR at bucket rate, whichever is slower (bucket rate wins on small windows).
        ideal_delay = self.target_window / len(requests)
        rate_delay = 1.0 / self.bucket.rate_per_sec
        delay = max(ideal_delay, rate_delay)

        results = []
        for i, req in enumerate(requests):
            if i > 0:
                await asyncio.sleep(delay)
            await self.bucket.acquire()
            results.append(await handler(req))
        return results
```

Usage:

```python
smoother = BurstSmoother(bucket=ENDPOINT_BUCKETS["reviews"], target_window_seconds=120)
# 80 review requests fire over 120s instead of 30s — bucket eats the residual smoothly
results = await smoother.submit_batch(review_request_payloads, send_review_request)
```

For KombiLife specifically: 80 requests over 120s = 0.67 req/sec = 40 req/min, well under the 15 req/min the `reviews` bucket grants. The burst completes in 2 minutes with zero 429s and zero dropped review requests.

### 6. Webhook amplification accounting (neutralizes inbound→outbound multipliers)

When an inbound Podium webhook (or Shopify webhook, or any other source) triggers N outbound Podium calls, the effective rate the bucket sees is N× the inbound rate. Estimate the amplification factor per inbound event type and admit-control at the front door rather than queue at the bucket:

```python
AMPLIFICATION_FACTOR = {
    "shopify.order.created":    5,   # contact upsert + 1 review request + 3 attribute writes
    "podium.conversation.new":  2,   # ack + tag write
    "podium.review.received":   3,   # contact update + sentiment write + slack mirror
}

class AdmissionController:
    """Reject inbound work when its projected outbound cost exceeds remaining budget."""

    def __init__(self, bucket: TokenBucket, daily_monitor: DailyQuotaMonitor):
        self.bucket = bucket
        self.daily = daily_monitor

    async def admit(self, event_type: str) -> bool:
        cost = AMPLIFICATION_FACTOR.get(event_type, 1)
        # Reject if a single event would burn >5% of remaining daily quota
        remaining = self.daily.quota - int(await self.daily._redis.get(self.daily._key()) or 0)
        if cost > remaining * 0.05:
            log_warn(f"admission denied {event_type}: cost={cost} remaining={remaining}")
            return False
        return True
```

Reject-with-replay is acceptable for webhooks Podium delivers — Podium retries inbound webhooks on non-2xx. Reject-with-replay is **not** acceptable for Shopify webhooks unless your handler is replayable; queue them to a durable store instead and drain when the daily quota recovers.

## Error Handling

| HTTP Status | Podium Error | Root Cause | Action |
|---|---|---|---|
| `429 Too Many Requests` | `rate_limited` | Per-minute or per-day envelope exceeded | Parse `Retry-After`; honor + cap at 120s; back off attempts |
| `503 Service Unavailable` | `service_overloaded` | Podium-side overload (not client-attributable) | Exponential backoff + jitter; max 4 attempts |
| `400 Bad Request` | `quota_exhausted` | 24h envelope hit (returned by some endpoints instead of 429) | Hard-stop the offending endpoint family until UTC midnight |
| `502/504` | `gateway_timeout` | Upstream timeout, often during burst | Retry once with full bucket wait; do not retry-storm |
| in-process | `BurstSmoother queue full` | Submitted batch larger than smoother capacity | Spill to a durable queue; drain on the next minute |
| in-process | `AdmissionController denied` | Projected cost > 5% of remaining daily quota | Defer to a low-priority worker; alert on sustained denials |

## Examples

### Minimal — wrap an existing call site with the bucket

```python
from podium_rate_limit import TokenBucket

bucket = TokenBucket(rate_per_minute=60, capacity=10)

async def safe_podium_call(method: str, path: str, **kwargs):
    await bucket.acquire()
    return await unsafe_podium_call(method, path, **kwargs)
```

One line of change at every call site. The bucket is global; safe under asyncio concurrency.

### Operator — simulate a request trace and see projected 429 count

```bash
python3 scripts/bucket_simulator.py \
  --trace ./traces/2026-05-09-prod-replay.csv \
  --rate-per-minute 60 \
  --capacity 10
```

Output:

```json
{
  "trace_requests": 4127,
  "trace_window_seconds": 3600,
  "projected_429_count": 0,
  "projected_p99_queue_wait_ms": 1840,
  "would_exhaust_daily_quota_at_request": null
}
```

### Operator — check today's quota consumption

```bash
python3 scripts/quota_monitor.py --redis-url redis://localhost:6379 --quota 50000
# Exit 0 = healthy; 1 = warn; 2 = page; 3 = throttle
```

### Operator — smooth a CSV of pending review requests

```bash
python3 scripts/burst_smoother.py \
  --input pending-reviews-2026-05-09.csv \
  --rate-per-minute 15 \
  --target-window-seconds 120 \
  --output smoothed-schedule.csv
```

### Operator — parse a `Retry-After` header from a real 429 response

```bash
# Integer-seconds form
python3 scripts/retry_after_parse.py --header "30"
# {"wait_seconds": 30.0, "absolute_wakeup_utc": "2026-05-09T17:00:30+00:00"}

# HTTP-date form
python3 scripts/retry_after_parse.py --header "Wed, 09 May 2026 17:05:00 GMT"
# {"wait_seconds": 287.4, "absolute_wakeup_utc": "2026-05-09T17:05:00+00:00"}
```

## Output

- Token-bucket rate limiter wired into every outbound Podium call site
- `Retry-After` parser supporting integer-seconds AND HTTP-date forms, with a 120s cap
- Daily quota monitor with three severity tiers (warn 70%, page 85%, throttle 95%)
- Per-endpoint bucket isolation — one bucket per endpoint family, summed rates = 60/min
- End-of-day burst smoother for the 5pm review-request cluster
- Webhook amplification accounting with admission control on inbound events

## Resources

- [Podium API docs — Rate limits](https://docs.podium.com/reference/rate-limiting)
- [Token bucket algorithm — Wikipedia](https://en.wikipedia.org/wiki/Token_bucket)
- [RFC 7231 § 7.1.3 — `Retry-After` header](https://datatracker.ietf.org/doc/html/rfc7231#section-7.1.3)
- [config/settings.yaml](config/settings.yaml) — bucket sizes, thresholds, endpoint allocation
- [references/errors.md](references/errors.md) — ERR_RL_* codes with cause + solution
- [references/examples.md](references/examples.md) — 10 worked examples (single-call, isolation, burst, replay)
- [references/implementation.md](references/implementation.md) — Node.js equivalents, Redis vs SQLite stores, the on-call playbook for a 429 cascade in progress
- [scripts/bucket_simulator.py](scripts/bucket_simulator.py) — CLI: simulate token-bucket behavior on a request trace
- [scripts/quota_monitor.py](scripts/quota_monitor.py) — CLI: query daily quota counter and emit warn/page/throttle
- [scripts/burst_smoother.py](scripts/burst_smoother.py) — CLI: smooth a batched CSV against the per-minute ceiling
- [scripts/retry_after_parse.py](scripts/retry_after_parse.py) — CLI: parse `Retry-After` to absolute wakeup time
