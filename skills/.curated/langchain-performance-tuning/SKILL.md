---
name: langchain-performance-tuning
description: "Tune LangChain 1.0 / LangGraph 1.0 Python chains and agents for throughput,\n\
  latency, and cost \u2014 streaming modes, explicit batch concurrency, semantic\n\
  plus exact caches, persistent message history, and async-safe retriever\npatterns.\
  \ Use when p95 latency exceeds target, batching \"does not work\",\ncost grows linearly\
  \ with traffic, or a process restart wipes chat history.\nTrigger with \"langchain\
  \ performance\", \"langchain slow batch\",\n\"langchain throughput\", \"langchain\
  \ p95 latency\", \"semantic cache hit rate\".\n"
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
- performance
- caching
- async
compatibility: Designed for Claude Code
---
# LangChain Performance Tuning

## Overview

An engineer calls `chain.batch(inputs_1000)` expecting 1000 parallel LLM calls. Actual behavior: `Runnable.batch` and `Runnable.abatch` in LangChain 1.0 default to `max_concurrency=1`, so the 1000 inputs run **sequentially with bookkeeping overhead** — sometimes slower than a plain `for` loop. This is pain-catalog entry P08. The fix is one line:

```python
# Before: serial, ~1000 * per_call_latency
await chain.abatch(inputs)

# After: 10x throughput at 10 providers' worth of concurrency
await chain.abatch(inputs, config={"max_concurrency": 10})
```

Other silent regressions in the same pain catalog: P48 (`invoke` inside `async def` blocks the FastAPI event loop), P22 (`InMemoryChatMessageHistory` loses every user's chat on restart), P62 (`RedisSemanticCache` at the default `score_threshold=0.95` returns under 5% hit rate), P59 (async retrievers leak connections on cancellation), P60 (`BackgroundTasks` fires *after* the response — wrong for per-token SSE), P01 (streaming token counts are only reliable on the `on_chat_model_end` event).

This skill wires a production performance baseline: explicit batch concurrency, async-only code paths, Redis-backed caches tuned on a golden set, persistent chat history with TTL, and TTFT instrumentation from `astream_events(version="v2")`.

## Prerequisites

- Python 3.11+ with `langchain>=1.0,<2`, `langgraph>=1.0,<2`, `langchain-openai` or `langchain-anthropic`, `langchain-community`, `langchain-redis` or `redis>=5`.
- A working LangChain 1.0 chain or LangGraph 1.0 graph that already passes functional tests.
- Redis 7+ reachable from the app for cache and history (local Docker is fine for dev).
- A FastAPI / Starlette async endpoint, or an equivalent async entrypoint.
- Observability: a place to emit metrics (Prometheus, OpenTelemetry, or LangSmith) — needed to measure TTFT, p95, and cache hit rate.

## Instructions

1. **Establish a latency budget and baseline.** Pick explicit targets before changing code: TTFT under 1s, p95 total under 5s, throughput over 20 req/s per worker, cost under $X per 1k interactions. Run a 5-minute load test with `locust` or `wrk` against the current chain and record p50 / p95 / p99 / TTFT / total cost. Without these numbers every downstream change is theater.

2. **Convert every hot path to async (P48).** Inside `async def` handlers, replace `invoke`, `stream`, `batch`, `get_relevant_documents`, and `tool.run` with `ainvoke`, `astream` / `astream_events(version="v2")`, `abatch`, `aget_relevant_documents`, and `tool.arun`. See `references/async-safety-checklist.md` for a grep pattern and a CI linter. Target: zero sync LangChain calls inside any async function.

3. **Fix `.abatch()` concurrency (P08).** Every `.abatch` / `.batch` call must pass `config={"max_concurrency": N}` where N is chosen from the provider table in `references/batch-concurrency-per-provider.md` (Anthropic 10-20, OpenAI 20-50, local vLLM 100+). For multi-worker deploys, cap account-wide calls with a LiteLLM / Portkey proxy or a Redis semaphore — `max_concurrency` only governs one process.

4. **Instrument TTFT with `astream_events(version="v2")` (P01).** Measure time to first token separately from total latency — user-perceived performance hinges on TTFT. Read usage metadata only on the `on_chat_model_end` event; per-chunk usage fields lag and are not reliable mid-stream.

   ```python
   from time import perf_counter
   async def run(chain, query: str):
       t0 = perf_counter(); ttft = None; tokens = 0
       async for ev in chain.astream_events({"input": query}, version="v2"):
           if ev["event"] == "on_chat_model_stream" and ttft is None:
               ttft = perf_counter() - t0
           if ev["event"] == "on_chat_model_end":
               tokens = ev["data"]["output"].usage_metadata["total_tokens"]
       return {"ttft_s": ttft, "total_s": perf_counter() - t0, "tokens": tokens}
   ```

5. **Enable an exact LLM cache.** For deterministic (temperature=0) prompts, set `RedisCache` or `SQLiteCache` globally. LangChain 1.0 keys include the bound tools signature (P61 fix), which prevents cache poisoning when an agent's tool list changes. Always set an explicit TTL on Redis keys — default Redis keys are immortal.

   ```python
   from langchain_core.globals import set_llm_cache
   from langchain_community.cache import RedisCache
   import redis
   set_llm_cache(RedisCache(redis.Redis.from_url("redis://cache:6379/0")))
   ```

6. **Add a semantic cache with a tuned threshold (P62).** The `RedisSemanticCache` default `score_threshold=0.95` produces < 5% hit rate on real traffic. Collect a 200-500 prompt golden set with labeled near-duplicates, measure cosine similarity with your embedding model, and pick the F1-maximizing threshold — typically **0.85-0.90** for `text-embedding-3-small`. Full procedure in `references/cache-tuning.md`. Do not run semantic cache behind `temperature > 0`; users will see prior random draws.

7. **Replace `InMemoryChatMessageHistory` (P22).** Every production chat path must use `RedisChatMessageHistory` (with `ttl`) or a LangGraph checkpointer (`AsyncPostgresSaver` / `AsyncSqliteSaver`). Add a restart test: mid-conversation, kill and restart the worker, assert the next user turn still sees prior messages. See `references/persistent-history.md` for migration steps and trim policies.

8. **Close retriever connection pools in FastAPI `lifespan` (P59).** Build the vector store once at startup, expose it via `app.state`, close it in the `finally` block. Never construct a retriever per request — cancellations leak pg connections.

9. **Stream tokens with SSE, not `BackgroundTasks` (P60).** `BackgroundTasks` runs after the response body is flushed; per-token dispatch via it delivers tokens the client will never read. Use `EventSourceResponse` (sse-starlette) or a WebSocket and pipe events from `astream_events`.

10. **Re-run the load test and diff the four metrics.** TTFT, p95, throughput, cost per 1k. If any regressed, revert that step and investigate — do not stack changes without verification. Execute in this order to isolate effects:

    1. Run the baseline load test and save results.
    2. Set `max_concurrency` on every `.abatch` call and re-run.
    3. Add exact cache, re-run, check cache hit rate.
    4. Configure semantic cache with tuned threshold, re-run, check hit rate again.
    5. Verify persistent history survives a worker restart.

### Throughput Tuning Table (starting values)

| Provider | Safe `max_concurrency` | Ceiling signal |
|----------|------------------------|-----------------|
| Anthropic (sonnet-4.5/4.6) | 10-20 | 429 `rate_limit_error` |
| OpenAI (gpt-4o / 4o-mini) | 20-50 | 429 + TPM exhaustion header |
| OpenAI o1 / reasoning | 2-5 | Cost + latency, not rate |
| Google Gemini 1.5/2.5 | 10-30 | 429 |
| Cohere | 20-40 | 429 |
| Local vLLM / TGI | 100-500 (batch N≈32-64) | GPU KV-cache OOM |
| Ollama on consumer GPU | 1-4 | Process queue backpressure |

### Latency Breakdown Template

Record these for every change, not just total:

| Metric | Target | Source |
|--------|--------|--------|
| TTFT p50 / p95 | 500ms / 1s | first `on_chat_model_stream` event |
| Total p50 / p95 | 2s / 5s | end-to-end handler |
| Tool-call p95 | < 1s per tool | `on_tool_end` - `on_tool_start` |
| Retriever p95 | < 300ms | `on_retriever_end` - `on_retriever_start` |
| Provider p95 | measure per model | split by LLM node |

### Batch Sweet-Spot Numbers

- Anthropic tier 2 chat: `max_concurrency=10` saturates at roughly 8 req/s, p95 doubles past 20.
- OpenAI `gpt-4o-mini` tier 3: knee of the curve around `max_concurrency=30-40`; ~40 req/s throughput.
- Local vLLM A100: server-side batch sweet spot `N=32-64`, client `max_concurrency=100+`.

Verify on your own account — these are starting points, not promises.

## Output

Deliverables from running this skill end-to-end:

- A `perf/` directory with `baseline.json` and `tuned.json` load-test results.
- All async handlers use `ainvoke` / `astream_events` / `abatch` with explicit `max_concurrency`.
- `set_llm_cache` wired to `RedisCache` (exact) and optionally `RedisSemanticCache` (tuned threshold).
- `RunnableWithMessageHistory` or LangGraph checkpointer backed by Redis or Postgres, with TTL.
- FastAPI `lifespan` closing vector store pools on shutdown.
- SSE endpoint streaming from `astream_events(version="v2")`.
- A `tests/test_no_sync_in_async.py` CI guard (see async-safety reference).
- Metrics exported: `ttft_seconds`, `total_latency_seconds`, `cache_hit_total`, `cache_miss_total`, `batch_concurrency_current`.
- Runbook entry with the tuned `max_concurrency` per provider and the semantic-cache threshold, versioned in git.

## Error Handling

| Symptom | Root cause | Fix |
|---------|-----------|-----|
| `.abatch(inputs)` no faster than a `for` loop | `max_concurrency=1` default (P08) | Pass `config={"max_concurrency": N}` |
| FastAPI TTFT collapses under load | Sync `invoke` inside `async def` (P48) | Switch to `ainvoke` / `astream_events` |
| Chat forgets prior turns after deploy | `InMemoryChatMessageHistory` (P22) | Move to `RedisChatMessageHistory` with TTL |
| Semantic cache hit rate < 5% | `score_threshold=0.95` default (P62) | Tune on golden set to 0.85-0.90 |
| pg pool exhausted hours into load test | Retriever not closed on cancel (P59) | Close vector store in FastAPI `lifespan` |
| SSE client sees zero tokens | Dispatching via `BackgroundTasks` (P60) | Use `EventSourceResponse` and `astream_events` |
| Per-chunk token counts fluctuate | Usage metadata lags during stream (P01) | Read only on `on_chat_model_end` |
| 429 storm after tuning concurrency | Per-worker limit * N workers > account RPM | Add LiteLLM/Portkey proxy or Redis semaphore |
| Semantic cache returns off-brand output | Cache hit on `temperature > 0` route | Disable semantic cache or force temperature=0 |
| Cache poisoning after tool change | Missing tools in cache key | Upgrade LangChain to 1.0.x post-P61 fix |

## Examples

**Example 1 — Fix a sequential batch job.**

```python
# Before — 1000 items, 18 minutes end-to-end
results = await chain.abatch(inputs)

# After — 1000 items, ~2 minutes; Anthropic tier-2 account, N=10
results = await chain.abatch(inputs, config={"max_concurrency": 10})
```

**Example 2 — Wire persistent history and an exact cache on a FastAPI app.**

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from langchain_core.globals import set_llm_cache
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.cache import RedisCache
from langchain_community.chat_message_histories import RedisChatMessageHistory
import redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    r = redis.Redis.from_url("redis://cache:6379/0")
    set_llm_cache(RedisCache(r))
    app.state.r = r
    yield
    r.close()

app = FastAPI(lifespan=lifespan)

def history_for(session_id: str) -> RedisChatMessageHistory:
    return RedisChatMessageHistory(
        session_id=session_id,
        url="redis://history:6379/2",
        ttl=60 * 60 * 24 * 14,
    )

chain_with_history = RunnableWithMessageHistory(
    base_chain, history_for,
    input_messages_key="input",
    history_messages_key="history",
)
```

**Example 3 — Stream tokens with measured TTFT.**

```python
from sse_starlette.sse import EventSourceResponse
from time import perf_counter

@app.post("/chat")
async def chat(req: ChatReq):
    async def gen():
        t0 = perf_counter()
        async for ev in chain_with_history.astream_events(
            {"input": req.text},
            config={"configurable": {"session_id": req.session_id}},
            version="v2",
        ):
            if ev["event"] == "on_chat_model_stream":
                yield {"data": ev["data"]["chunk"].content}
        app.state.r.incrbyfloat("ttft_sum_s", perf_counter() - t0)
    return EventSourceResponse(gen())
```

## Resources

- [One-pager](references/one-pager.md) — problem / solution / key features snapshot.
- [batch-concurrency-per-provider](references/batch-concurrency-per-provider.md) — per-provider `max_concurrency` table, sweep procedure, semaphore patterns.
- [cache-tuning](references/cache-tuning.md) — exact vs semantic, Redis key design, golden-set threshold procedure, TTL strategy.
- [persistent-history](references/persistent-history.md) — Redis / Postgres / LangGraph checkpointer migration off `InMemoryChatMessageHistory`.
- [async-safety-checklist](references/async-safety-checklist.md) — sync-in-async grep + linter, lifespan pool cleanup, SSE vs `BackgroundTasks`.
- [LangChain streaming / batching](https://python.langchain.com/docs/how_to/streaming/#batching) — official docs for `Runnable.batch` and streaming modes.
- [LangChain caching](https://python.langchain.com/docs/how_to/llm_caching/) — `set_llm_cache`, Redis and SQLite backends.
- [LangGraph checkpointers](https://langchain-ai.github.io/langgraph/how-tos/persistence/) — persistence for graph state.
- Companion skills in `langchain-py-pack`: `langchain-model-inference` (token accounting), `langchain-embeddings-search` (retrieval tuning), `langchain-middleware-patterns` (tool-signature cache keying, P61).
