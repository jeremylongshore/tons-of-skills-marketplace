---
name: langchain-rate-limits
description: "Rate-limit LangChain 1.0 calls correctly across multi-worker deployments\
  \ \u2014\nRedis-backed limiters, asyncio.Semaphore, narrow exception whitelists,\
  \ and\nprovider-specific throttle handling. Use when hitting 429s in production,\n\
  scaling workers horizontally, or tuning throughput against Anthropic, OpenAI,\n\
  or Gemini tier limits.\nTrigger with \"langchain rate limit\", \"langchain 429\"\
  , \"langchain semaphore\",\n\"langchain token bucket\", \"anthropic rpm\", \"openai\
  \ rpm throttling\",\n\"InMemoryRateLimiter\", \"redis rate limiter\".\n"
allowed-tools: Read, Write, Edit, Bash(python:*), Bash(redis-cli:*)
version: 2.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- langchain
- langgraph
- python
- langchain-1.0
- rate-limits
- throttling
- concurrency
compatibility: Designed for Claude Code
---
# LangChain Rate Limits (Python)

## Overview

A team deploys 10 Cloud Run workers. Each worker initializes its `ChatAnthropic`
with `InMemoryRateLimiter(requests_per_second=10)` — they read the docs, they
picked a safe-looking number, they shipped. Thirty seconds later the dashboard
lights up with 429s: the cluster is pushing 100 RPS to Anthropic's 50 RPM
tier-1 ceiling, not the 10 RPS they configured. The name is the fix —
`InMemoryRateLimiter` is **in-process**. Each worker has its own counter. Ten
workers × 10 RPS = 100 RPS to the provider. This is pain-catalog entry **P29**
and it lands on every team that scales past one pod.

Three more traps wait on the same code path:

- **P07** — `.with_fallbacks([backup])` defaults `exceptions_to_handle=(Exception,)`,
  which on Python <3.12 swallows `KeyboardInterrupt`. Ctrl+C during a 429
  retry storm silently falls through to the backup chain and keeps billing.
- **P30** — `ChatOpenAI` and `ChatAnthropic` default `max_retries=6`. That is
  retries, not attempts: **7 total requests per logical call** on flaky
  networks. One `.invoke()` can bill 7x.
- **P31** — Anthropic's RPM counts cache reads, cache writes, and uncached
  calls **uniformly**. Cache-heavy workloads at 50 RPM can 429 on cache writes
  while the ITPM dashboard shows headroom.

This skill covers measuring demand before picking a limit; the
`InMemoryRateLimiter` vs Redis-backed limiter vs `asyncio.Semaphore` decision
tree; the narrow `exceptions_to_handle` whitelist; `max_retries=2` math; and
the provider-specific limit taxonomy (RPM, ITPM, OTPM, concurrent,
cached-vs-uncached). Pin: `langchain-core 1.0.x`, `langchain-anthropic 1.0.x`,
`langchain-openai 1.0.x`. Pain-catalog anchors: **P07, P08, P29, P30, P31**.
For `.batch(max_concurrency=...)` tuning, see the sibling skill
`langchain-performance-tuning` — this skill is about provider-facing rate caps.

## Prerequisites

- Python 3.10+ (3.12+ fixes the `KeyboardInterrupt` half of P07)
- `langchain-core >= 1.0, < 2.0`
- At least one provider: `pip install langchain-anthropic langchain-openai`
- For multi-worker prod: `redis >= 4.5` client and a Redis server reachable from every worker
- Completed `langchain-model-inference` — the chat-model factory from that skill is where `rate_limiter=` gets attached

## Instructions

### Step 1 — Measure actual demand before picking a number

**Do not guess at `requests_per_second`.** Instrument first, size second.
Attach a `BaseCallbackHandler` that logs per-call `input_tokens`,
`output_tokens`, and `cache_read_input_tokens` from `response.generations[].message.usage_metadata`:

```python
chain.with_config({"callbacks": [DemandLogger()]})
```

Collect 24-48 hours of representative traffic. Roll up: p50 and p95 RPM, p95
ITPM, p95 OTPM, cache hit rate. Size the limiter at **70% of the binding
constraint's tier ceiling** on your p95.

See [Measuring Demand](references/measuring-demand.md) for the full
`DemandLogger` implementation, pandas roll-up, OTEL integration, load-test
harness, and multi-tenant sizing strategies.

### Step 2 — `InMemoryRateLimiter` for single-process dev only; never multi-worker prod

LangChain 1.0 ships `InMemoryRateLimiter` as a first-class `BaseChatModel` parameter:

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.rate_limiters import InMemoryRateLimiter

limiter = InMemoryRateLimiter(
    requests_per_second=0.58,    # 35 RPM = 70% of Anthropic tier-1 50 RPM
    check_every_n_seconds=0.1,
    max_bucket_size=5,           # burst capacity
)

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    rate_limiter=limiter,
    max_retries=2,
    timeout=30,
)
```

**`InMemoryRateLimiter` is per-process.** Safe for:

- Single-process local dev (`python script.py`)
- Single-worker uvicorn (`uvicorn --workers 1`)
- Jupyter notebooks, batch scripts

**Unsafe for** (this is P29):

- Multi-worker uvicorn / gunicorn (`--workers 4`)
- Any container orchestrator with replica count > 1 (Cloud Run min-instances > 1, K8s, ECS)
- Distributed job runners (Celery, Temporal, Cloud Tasks fanout)

### Step 3 — Redis-backed limiter for cluster-wide enforcement

For multi-worker deployments, cluster-wide rate limiting requires shared state.
Redis is the default answer — atomic Lua script for sliding-window, or Redis
6.2+ `CL.THROTTLE` for GCRA.

```python
import redis
from langchain_anthropic import ChatAnthropic
# RedisRateLimiter class defined in references/redis-limiter-pattern.md
from your_app.limiters import RedisRateLimiter

client = redis.Redis.from_url("redis://redis.internal:6379/0")

limiter = RedisRateLimiter(
    client,
    key="anthropic:prod",
    requests_per_second=35 / 60,  # 35 RPM cluster-wide, not per-worker
)

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    rate_limiter=limiter,
    max_retries=2,
    timeout=30,
)
```

**Key scoping decisions:**

- `key="anthropic:prod"` — all tenants share one global budget (simplest)
- `key=f"anthropic:tenant:{tenant_id}"` — per-tenant quota (requires cleanup for dead tenants)
- Two-level: per-tenant + global, acquire both (best for multi-tenant SaaS)

See [Redis Limiter Pattern](references/redis-limiter-pattern.md) for the full
`RedisRateLimiter` implementation (atomic Lua sliding window), the GCRA
alternative via `CL.THROTTLE`, failure modes (Redis down, clock skew), and
per-tenant cleanup strategy.

### Step 4 — `asyncio.Semaphore` for per-worker in-flight concurrency cap

The rate limiter throttles **request rate**. A semaphore throttles **in-flight
count**. Use both:

```python
import asyncio

# Cluster: 35 RPM (Redis enforces)
# Worker: 20 in-flight at once (semaphore enforces)
worker_sem = asyncio.Semaphore(20)

async def bounded_invoke(inp):
    async with worker_sem:
        return await llm.ainvoke(inp)

# Fanout
results = await asyncio.gather(*[bounded_invoke(x) for x in inputs])
```

Why both: a semaphore prevents a single worker from queueing hundreds of
pending limiter acquires against Redis (head-of-line blocking on the event
loop). The limiter prevents the cluster from exceeding the provider tier. They
solve different problems.

**Semaphore sizing**: target latency-bandwidth-product. If p95 request latency
is 2s and the worker's RPS cap is 10, in-flight count ≈ 2 × 10 = 20. Overshoot
is wasted memory; undershoot leaves throughput on the table.

### Step 5 — Narrow `with_fallbacks(exceptions_to_handle=...)` — never `(Exception,)`

`.with_fallbacks([backup])` defaults to catching `Exception`. This is P07 — on
Python <3.12, `Exception` edge-cases include `KeyboardInterrupt` propagation.
Ctrl+C during a retry storm silently hands off to the backup and keeps running.
**Always narrow the tuple:**

```python
from anthropic import (
    RateLimitError, APITimeoutError, APIConnectionError, InternalServerError,
)

resilient = (prompt | claude | parser).with_fallbacks(
    [prompt | gpt4o | parser],
    exceptions_to_handle=(
        RateLimitError, APITimeoutError,
        APIConnectionError, InternalServerError,
    ),
    # NEVER: Exception, BaseException, AuthenticationError,
    # BadRequestError, ValidationError
)
```

The whitelist is **only transient provider errors**. `AuthenticationError`,
`BadRequestError`, and `ValidationError` are bugs in your code/credentials —
fallback produces the same crash. See the sibling skill's reference
`langchain-sdk-patterns/references/fallback-exception-list.md` for the full
per-provider whitelist (Anthropic, OpenAI, Gemini).

### Step 6 — `max_retries=2`, never the default `max_retries=6`

`max_retries` is **retries, not attempts.** Default `max_retries=6` on
`ChatOpenAI` / `ChatAnthropic` means **initial + 6 retries = 7 billed requests**
per logical call (P30). On a flaky network, one `.invoke()` costs 7x what you
budgeted.

```python
# BAD — default
llm = ChatOpenAI(model="gpt-4o")  # max_retries=6

# GOOD — production default
llm = ChatOpenAI(
    model="gpt-4o",
    max_retries=2,      # initial + 2 retries = 3 total billed requests max
    timeout=30,
    rate_limiter=redis_limiter,
)
```

Trade resilience off to the fallback layer — `with_fallbacks` is strictly
cheaper than retry amplification when the primary is genuinely unhealthy.
Instrument retry count via callback and alert if retry rate exceeds ~5%.

See [Backoff and Retry](references/backoff-and-retry.md) for the full math,
`Retry-After` header handling, and circuit-breaker pattern for sustained
overload.

### Step 7 — Understand the provider limit taxonomy

Different providers expose different limit types. Know which one binds your
workload before you size:

| Limit | Meaning | Who enforces | Binds for |
|---|---|---|---|
| **RPM** | Requests/minute (counts every call) | All three providers | Short chat replies |
| **ITPM** | Input tokens/minute | Anthropic, OpenAI (as TPM combined) | Long document Q&A |
| **OTPM** | Output tokens/minute | Anthropic separately; OpenAI as combined TPM | Long completions |
| **Concurrent** | In-flight request cap | Mainly OpenAI higher tiers | Burst traffic |
| **Cached reads** | Cache-read input tokens (Anthropic) | Anthropic separate budget line | Cache-heavy workloads (but still counts toward RPM — P31) |

Critical for Anthropic cache workloads (P31): RPM counts uniformly across
cached reads, cache writes, and uncached calls. A workload at 90% cache hit
rate still trips the 50 RPM ceiling at 51 requests/min. Separate monitors for
`cache_read_input_tokens` vs `input_tokens` (minus cache read/write) give
early warning.

### Step 8 — Decision tree: which limiter to use

```
┌─ Single process (dev, notebooks, sync CLI, --workers 1)?
│  └─ InMemoryRateLimiter
│
├─ Multi-process but single host (same-machine pool, local gunicorn)?
│  └─ Redis-backed limiter (even localhost Redis beats InMemoryRateLimiter —
│     which still has per-process counters)
│
├─ Multi-host cluster (Cloud Run --min-instances>1, K8s, ECS)?
│  └─ Redis-backed limiter (mandatory)
│
├─ Multi-region or cross-cloud?
│  └─ Regional Redis per zone + provider-side account quota
│     (cross-region Redis latency adds 30-200ms per acquire)
│
└─ Any of the above + multi-tenant SaaS?
   └─ Two-level Redis limiter: per-tenant + global, acquire both
```

Always pair with `asyncio.Semaphore(N)` per-worker for in-flight concurrency.

### Step 9 — Provider tier snapshot (verify before shipping)

**2026-04-21 snapshot — re-verify against the official console before shipping.**

| Provider | Free tier RPM | Tier-1 RPM | High tier RPM | Source |
|---|---|---|---|---|
| Anthropic | 5 | 50 (Build 1) | 4000 (Build 4) | https://platform.claude.com/docs/en/api/rate-limits |
| OpenAI | 3 | 500 | 10000 (Tier 5) | https://platform.openai.com/docs/guides/rate-limits |
| Google Gemini | 15 | 2000 (Paid 1) | 30000 (Paid 3) | https://ai.google.dev/gemini-api/docs/rate-limits |

Tiers change quarterly. A limiter sized six months ago on a different tier is
a liability. See [Provider Tier Matrix](references/provider-tier-matrix.md) for
the full matrix including ITPM / OTPM / cached-read separation, binding-limit
math, and the pre-ship verification checklist.

## Output

- Instrumented `DemandLogger` callback attached to your chains for 24-48h before sizing
- `InMemoryRateLimiter` in dev / notebooks / single-worker only
- `RedisRateLimiter` (sliding-window Lua or `CL.THROTTLE` GCRA) for any multi-worker deployment, keyed per-tenant or global
- `asyncio.Semaphore(N)` per-worker in-flight cap paired with the cluster-wide limiter
- `max_retries=2` on every `ChatAnthropic` / `ChatOpenAI` / `ChatGoogleGenerativeAI`
- `.with_fallbacks(exceptions_to_handle=(RateLimitError, APITimeoutError, APIConnectionError, InternalServerError))` — never `(Exception,)`
- Per-provider tier re-verified from the official console, sized at 70% of the binding constraint

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| `anthropic.RateLimitError: 429 THROTTLED` at cluster RPM = N × InMemoryRateLimiter ceiling | `InMemoryRateLimiter` is per-process; N workers each send at their limit (P29) | Switch to Redis-backed limiter (Step 3) |
| 429 on cache writes while ITPM dashboard shows headroom | Anthropic RPM counts cache writes uniformly (P31) | Budget at RPM level with limiter; separate cached vs uncached metrics |
| One `.invoke()` bills as 7 requests on flaky networks | Default `max_retries=6` (P30) | `max_retries=2` + fallback layer for resilience |
| `Ctrl+C` during retry storm silently falls through to backup chain | `exceptions_to_handle=(Exception,)` catches `KeyboardInterrupt` on Python <3.12 (P07) | Narrow tuple to `(RateLimitError, APITimeoutError, APIConnectionError, InternalServerError)` |
| Limiter queue p95 wait > 500ms | Limiter is oversubscribed for real traffic | Re-measure demand (Step 1); upgrade provider tier OR shed load |
| `redis.exceptions.ConnectionError` blocks all LLM calls | Redis unavailable and limiter is fail-closed | Instrument Redis health; decide fail-open (log loudly) vs fail-closed (shed load) — for provider safety, prefer fail-closed |
| `retry-after` header climbing 2→4→8→16 | Pushing past tier; backoff amplifying, not absorbing | Lower limiter target RPS by 20%; upgrade tier if sustained |
| `google.api_core.exceptions.ResourceExhausted` on Gemini | Gemini free tier 15 RPM is brutal | Upgrade to paid Gemini tier 1 (2000 RPM) or use Redis limiter at 10 RPM |

## Examples

### Multi-worker Cloud Run deployment with Anthropic tier-1 50 RPM

Ten workers, single region, Redis in same VPC. Target: 35 RPM cluster-wide
(70% of 50 RPM ceiling), 20 in-flight per worker.

```python
import asyncio, os, redis
from langchain_anthropic import ChatAnthropic
from anthropic import (
    RateLimitError, APITimeoutError, APIConnectionError, InternalServerError,
)
from your_app.redis_limiter import RedisRateLimiter  # see references

_client = redis.Redis.from_url(os.environ["REDIS_URL"])
anthropic_limiter = RedisRateLimiter(
    _client, key="anthropic:prod",
    requests_per_second=35 / 60,    # 35 RPM cluster-wide
)

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    rate_limiter=anthropic_limiter, # cluster gate
    max_retries=2,                  # not 6 (P30)
    timeout=30,
)

chain = (prompt | llm | parser).with_fallbacks(
    [prompt | gpt4o_backup | parser],
    exceptions_to_handle=(          # narrow tuple (P07)
        RateLimitError, APITimeoutError,
        APIConnectionError, InternalServerError,
    ),
)

worker_sem = asyncio.Semaphore(20)  # per-worker in-flight cap
async def invoke_bounded(inp):
    async with worker_sem:
        return await chain.ainvoke(inp)
```

Cluster behavior: every worker's limiter call hits the same Redis key. At 35
RPM cluster-wide, individual workers see fair-share throughput. `max_retries=2`

- narrow fallback tuple means transient 429s surface quickly and hand off to
GPT-4o instead of amplifying cost.

### Multi-tenant SaaS with per-tenant isolation

Two-level Redis limiter. Per-tenant limit prevents noisy neighbors; global limit
protects the provider tier.

See [Redis Limiter Pattern](references/redis-limiter-pattern.md) for the
two-level acquire implementation (acquire tenant key first, then global key;
release tenant if global fails) and the per-tenant cleanup cron.

### Single-process dev — `InMemoryRateLimiter` is fine

For local debugging, notebook work, or a sync CLI tool:

```python
from langchain_core.rate_limiters import InMemoryRateLimiter

limiter = InMemoryRateLimiter(requests_per_second=0.5, max_bucket_size=3)
llm = ChatAnthropic(model="claude-sonnet-4-6", rate_limiter=limiter, max_retries=2)
```

Do not carry this into production without re-reading Step 2.

## Resources

- [LangChain how-to: Chat model rate limiting](https://python.langchain.com/docs/how_to/chat_model_rate_limiting/)
- [`InMemoryRateLimiter` API](https://python.langchain.com/api_reference/core/rate_limiters/langchain_core.rate_limiters.InMemoryRateLimiter.html)
- [Anthropic rate limits](https://platform.claude.com/docs/en/api/rate-limits)
- [OpenAI rate limits](https://platform.openai.com/docs/guides/rate-limits)
- [Google Gemini rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Redis `CL.THROTTLE` (redis-cell module)](https://github.com/brandur/redis-cell)
- Pack pain catalog: `docs/pain-catalog.md` (entries P07, P08, P29, P30, P31)
- Sibling skills: `langchain-sdk-patterns` (batch concurrency, fallback exception whitelist), `langchain-performance-tuning` (`.batch(max_concurrency=...)` tuning for throughput)
