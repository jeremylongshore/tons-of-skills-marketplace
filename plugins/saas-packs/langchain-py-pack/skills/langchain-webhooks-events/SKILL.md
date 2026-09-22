---
name: langchain-webhooks-events
description: "Dispatch LangChain 1.0 chain/agent events to external systems \u2014\
  \ webhooks, Kafka,\nRedis Streams, SNS \u2014 via async fire-and-forget callbacks,\
  \ subgraph-aware wiring,\nand HMAC-signed delivery with idempotency keys. Use when\
  \ firing webhooks on tool\ncalls, pushing telemetry to Kafka / Redis Streams, or\
  \ fanning progress to multiple\nsubscribers without blocking the chain.\nTrigger\
  \ with \"langchain webhook\", \"langchain event dispatch\", \"langchain callback\
  \ kafka\",\n\"langchain pubsub\", \"langchain per-tool webhook\", \"BaseCallbackHandler\
  \ webhook\",\n\"on_tool_end webhook\", \"langchain analytics event\".\n"
allowed-tools: Read, Write, Edit, Bash(python:*)
version: 2.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- langchain
- langgraph
- python
- langchain-1.0
- webhooks
- async
- events
- callbacks
compatibility: Designed for Claude Code
---
# LangChain Webhooks and Event Dispatch (Python)

## Overview

A team wires per-tool webhook dispatch from their LangChain agent via FastAPI
`BackgroundTasks` — analytics is always N seconds late because `BackgroundTasks`
fire **after** the HTTP response closes, not during the stream (P60). Worse:
the `BaseCallbackHandler` they attached via `.with_config(callbacks=[h])`
fires on the outer agent but is dark on the subagent's tool calls — custom
callbacks are **not** inherited by LangGraph subgraphs (P28), they must be
passed via `config["callbacks"]` at invoke time.

Pain-catalog anchors handled here:

- P28 — Callbacks via `with_config` don't propagate to subgraphs
- P46 — SSE streams dropped by buffering proxies (see `langchain-langgraph-streaming`)
- P47 — `astream_events(v2)` emits thousands of events; never forward raw
- P48 — Sync `invoke()` inside async endpoint blocks the event loop
- P60 — `BackgroundTasks` fire post-response; wrong for per-event dispatch

This skill walks through an async `AsyncCallbackHandler` with fire-and-forget
dispatch, per-target sinks for HTTP / Kafka / Redis Streams / SNS, HMAC-signed
delivery with 1s/5s/30s retry and DLQ, idempotency keys = `run_id + event_type

- step_index`, and`config["callbacks"]` wiring that makes subagent calls visible.
Typical webhook latency budget: <500ms per event. Pin: `langchain-core 1.0.x`,
`langgraph 1.0.x`. Scope: server-to-server dispatch only — UI streaming is in
`langchain-langgraph-streaming`.

## Prerequisites

- Python 3.10+
- `langchain-core >= 1.0, < 2.0`, `langgraph >= 1.0, < 2.0`
- `httpx >= 0.27` for async HTTP (or `aiohttp`)
- One of: `aiokafka`, `redis[hiredis] >= 5`, `aioboto3` (per target)
- An event sink — a webhook endpoint, Kafka topic, Redis Stream, or SNS topic
- A shared secret (for HMAC) stored in your secret manager, not env

## Instructions

### Step 1 — Write an async handler that fire-and-forget dispatches

Sync dispatch from a callback blocks the chain — a slow HTTP POST during
`on_tool_end` serializes all downstream tokens behind it (P48). Use
`asyncio.create_task(...)` so the dispatch runs alongside the chain:

```python
import asyncio
import uuid
from typing import Any
from langchain_core.callbacks import AsyncCallbackHandler

class EventDispatchHandler(AsyncCallbackHandler):
    """Fire-and-forget dispatch to external sinks.

    IMPORTANT: subclass AsyncCallbackHandler (not BaseCallbackHandler) so
    on_* methods are awaited. Mixing sync and async handlers is a silent
    footgun — sync on_* blocks the event loop (P48).
    """

    def __init__(self, sink, *, run_id: str | None = None):
        self.sink = sink                      # dispatch target — Step 3
        self.run_id = run_id or str(uuid.uuid4())
        self._tasks: set[asyncio.Task] = set()

    def _dispatch(self, event_type: str, payload: dict, step_index: int) -> None:
        # Fire-and-forget. Keep a strong reference so the task isn't GC'd
        # mid-flight (asyncio quirk — orphan tasks get garbage-collected).
        task = asyncio.create_task(
            self.sink.send(
                idempotency_key=f"{self.run_id}:{event_type}:{step_index}",
                event_type=event_type,
                payload=payload,
            )
        )
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def on_tool_end(self, output: Any, *, run_id, parent_run_id=None, **kwargs):
        # 4000 char cap — keep payload under typical webhook body limits
        # while preserving enough context for downstream analytics.
        MAX_OUTPUT_CHARS = 4000
        self._dispatch(
            "tool_end",
            {"output": str(output)[:MAX_OUTPUT_CHARS], "run_id": str(run_id)},
            step_index=kwargs.get("tags", []).__len__() or 0,
        )

    async def on_chain_end(self, outputs: dict, *, run_id, **kwargs):
        # Only named chains — skip the unnamed LCEL inner nodes (P47)
        name = kwargs.get("name")
        if not name or name.startswith("RunnableLambda"):
            return
        self._dispatch("chain_end", {"name": name, "run_id": str(run_id)}, step_index=0)

    async def drain(self, timeout: float = 5.0) -> None:
        """Call before process exit so in-flight dispatches complete."""
        if self._tasks:
            await asyncio.wait(self._tasks, timeout=timeout)
```

See [Async Callback Handler](references/async-callback-handler.md) for the full
handler — `on_llm_end`, filtering, sync-vs-async decision.

### Step 2 — Pass callbacks via `config` so subgraphs inherit them

P28: `Runnable.with_config(callbacks=[h])` binds at definition and is **not**
inherited by LangGraph subgraphs. Pass callbacks via `config` at invocation:

```python
# WRONG — subagent tool calls never fire the handler
agent_with_handler = agent.with_config({"callbacks": [handler]})
await agent_with_handler.ainvoke({"messages": [...]})

# RIGHT — callbacks in config propagate into subgraphs
await agent.ainvoke(
    {"messages": [...]},
    config={"callbacks": [handler], "configurable": {"thread_id": "t1"}},
)
```

Validate propagation with a probe that counts events by `kwargs["name"]` and
asserts the subagent's name appears. See [Subgraph Propagation](references/subgraph-propagation.md).

### Step 3 — Pick a dispatch target by delivery semantics

Match the event to the transport:

| Target | Delivery | Typical latency | Use when | Failure mode |
|---|---|---|---|---|
| HTTP webhook | At-least-once (with retry) | 50-500ms | Partner integrations, Zapier/Make, customer-owned endpoints | Endpoint 5xx → retry 1s/5s/30s → DLQ |
| Kafka (aiokafka) | At-least-once (idempotent producer) | 5-20ms intra-region | High-volume telemetry, analytics fan-in | Broker unavailable → retry + local buffer |
| Redis Streams (`XADD`) | At-least-once (consumer groups) | 1-5ms | Near-realtime worker queues, progress fan-out | Redis down → retry or spill to disk |
| SNS | At-most-once (best-effort) | 10-100ms | Fan-out to multiple SQS/Lambda subscribers | Best-effort only; accept loss or front with SQS FIFO |

Handler stays provider-agnostic; only the `sink` changes. A minimal HTTP sink:

```python
import hashlib, hmac, json, os
import httpx

WEBHOOK_URL = os.environ["WEBHOOK_URL"]
SIGNING_SECRET = os.environ["WEBHOOK_SIGNING_SECRET"].encode()

class WebhookSink:
    # 256-bit HMAC — industry-standard signature strength (GitHub, Stripe use same)
    SIG_ALG = hashlib.sha256
    # Retry schedule: 1s absorbs transient blips, 5s absorbs brief 503s,
    # 30s absorbs autoscaler / cold-start incidents. Beyond 30s = stale event.
    RETRY_DELAYS = (1, 5, 30)
    REQUEST_TIMEOUT_S = 5.0

    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def send(self, *, idempotency_key: str, event_type: str, payload: dict) -> None:
        body = json.dumps({"event": event_type, "data": payload}, sort_keys=True).encode()
        sig = hmac.new(SIGNING_SECRET, body, self.SIG_ALG).hexdigest()
        headers = {
            "Content-Type": "application/json",
            "Idempotency-Key": idempotency_key,
            "X-Signature-256": f"sha256={sig}",
        }
        for delay in self.RETRY_DELAYS:
            try:
                resp = await self.client.post(WEBHOOK_URL, content=body, headers=headers, timeout=self.REQUEST_TIMEOUT_S)
                if 200 <= resp.status_code < 300:
                    return
                if resp.status_code < 500 and resp.status_code != 429:
                    return  # 4xx (except 429) is not retryable
            except (httpx.TimeoutException, httpx.TransportError):
                pass
            await asyncio.sleep(delay)
        await self._dead_letter(idempotency_key, event_type, payload)
```

See [Dispatch Targets](references/dispatch-targets.md) for Kafka / Redis Streams
/ SNS sinks and per-target DLQ patterns.

### Step 4 — Filter events so you don't saturate the downstream

`astream_events(version="v2")` emits thousands of events per invocation (P47).
Never forward raw — dispatch only what the downstream consumes:

| Callback method | Typical decision | Why |
|---|---|---|
| `on_llm_start` | Skip | Prompt content often contains PII; low value without masking |
| `on_llm_new_token` | **Skip for dispatch** (UI only) | 1 event per token; N/A to analytics |
| `on_llm_end` | Dispatch for named chains only | Token usage, final response — high value, low volume |
| `on_chain_start` | Skip (P47 noise) | LCEL emits one per inner runnable |
| `on_chain_end` | Dispatch for named subgraphs only | Stage completion — what analytics cares about |
| `on_tool_start` | Optional (dispatch for audit log) | Matters for compliance / tool-use audit |
| `on_tool_end` | **Dispatch always** | The key analytics signal in agent flows |
| `on_agent_action` | Dispatch | Cleaner signal than `on_tool_start` in agent graphs |
| `on_agent_finish` | Dispatch | Terminal event for the run |

Rule of thumb: dispatch `on_tool_end` + named `on_chain_end` + `on_llm_end`.
Everything else is noise.

### Step 5 — Build idempotency keys and a retry budget

At-least-once transports mean duplicates. Build the key deterministically:

```python
# run_id — unique per chain invocation (propagates into subgraphs)
# event_type — on_tool_end / on_chain_end / on_llm_end
# step_index — monotonic per-run counter you maintain in the handler

idempotency_key = f"{run_id}:{event_type}:{step_index}"
```

Retry budget: **1s → 5s → 30s** (~36s total) then DLQ. Retry on 5xx / 429 /
network only — 4xx (except 429) goes straight to DLQ. DLQ is a Redis Stream
or S3 prefix keyed by `YYYY/MM/DD/run_id/idempotency_key.json`; alarm on depth
growth. See [Idempotency and Retry](references/idempotency-and-retry.md) for
HMAC verify, at-least-once vs at-most-once, and 24h de-dup window sizing.

### Step 6 — Never dispatch from `BackgroundTasks` (P60)

FastAPI `BackgroundTasks` run *after* the response closes — exactly wrong for
per-event dispatch. Events must go out *during* the chain:

```python
# WRONG — events fire all at once after the stream ends
@app.post("/chat")
async def chat(req: Request, bg: BackgroundTasks):
    bg.add_task(agent.ainvoke, {"messages": [...]})  # late + no streaming
    return {"status": "accepted"}

# RIGHT — handler fires during the chain, each on_tool_end dispatches immediately
@app.post("/chat")
async def chat(req: ChatReq):
    handler = EventDispatchHandler(sink=webhook_sink, run_id=req.run_id)
    try:
        result = await agent.ainvoke(
            {"messages": req.messages},
            config={"callbacks": [handler], "configurable": {"thread_id": req.thread_id}},
        )
    finally:
        await handler.drain(timeout=5.0)  # flush in-flight dispatches
    return {"result": result}
```

`drain()` awaits in-flight `asyncio.create_task()` dispatches up to 5s so
events aren't lost when the pod scales down mid-request.

## Output

- Async `BaseCallbackHandler` subclass with `asyncio.create_task()` fire-and-forget
- Callbacks wired via `config["callbacks"]` at invoke time (subgraph-safe)
- Per-target sink abstraction: HTTP / Kafka / Redis Streams / SNS
- HMAC-signed webhook payloads with 1s/5s/30s retry and DLQ fallback
- Idempotency key = `run_id + event_type + step_index`
- Event-taxonomy filter: dispatch `on_tool_end` + named `on_chain_end` + `on_llm_end`
- `drain()` on shutdown to flush in-flight dispatches

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| Handler fires on outer agent but not subagent | Bound via `with_config` at definition (P28) | Pass via `config["callbacks"]` at `invoke(...)` time |
| Webhook analytics lags generation duration | `BackgroundTasks` fire post-response (P60) | Dispatch from the callback handler, never from `BackgroundTasks` |
| Browser / Kafka saturates on long generations | Forwarded `astream_events(v2)` raw (P47) | Filter events server-side; dispatch only `on_tool_end`/`on_chain_end`/`on_llm_end` |
| SSE stream hangs, no end event | Proxy buffering (P46) | Set `X-Accel-Buffering: no` — see `langchain-langgraph-streaming` |
| Event loop freezes on slow webhook | Sync POST in callback (P48) | Subclass `AsyncCallbackHandler`; use `asyncio.create_task()` |
| Duplicate events downstream | At-least-once dispatch + retry | Receiver dedupes on `Idempotency-Key` header with 24h cache |
| Orphan `asyncio.create_task` never runs | GC collected the task | Hold a strong reference in `self._tasks` and discard on completion |
| Events lost on pod shutdown | In-flight tasks cancelled | Call `await handler.drain(timeout=5.0)` in endpoint `finally` block |
| 4xx webhook errors retrying 3x | Retry logic retrying everything | Retry only on 5xx / 429 / network; 4xx goes straight to DLQ |
| Signature verification fails on receiver | Body re-serialized with different key order | Sign the exact bytes you send; use `sort_keys=True` in `json.dumps` |

## Examples

### Named subgraph dispatch with a LangGraph agent

Planner subagent runs `search_docs` → `summarize`; outer agent needs a webhook
on `summarize` completion. Full wiring in [Subgraph Propagation](references/subgraph-propagation.md).

### Fan-out: webhook + Kafka + Redis Streams in one invocation

`CompositeSink` dispatches to multiple child sinks via
`asyncio.gather(..., return_exceptions=True)` — one sink's failure doesn't block
others. See [Dispatch Targets](references/dispatch-targets.md).

### HMAC-signed webhook receiver with de-dup

Verify `X-Signature-256`, SETNX `Idempotency-Key` against Redis with 24h TTL,
200 on both replay and first-seen. See [Idempotency and Retry](references/idempotency-and-retry.md).

## Resources

- [LangChain callbacks concepts](https://python.langchain.com/docs/concepts/callbacks/)
- [`BaseCallbackHandler` / `AsyncCallbackHandler` API](https://python.langchain.com/api_reference/core/callbacks/langchain_core.callbacks.base.BaseCallbackHandler.html)
- [`astream_events` v2 events reference](https://python.langchain.com/docs/how_to/streaming/#using-stream-events)
- [LangGraph streaming concepts](https://langchain-ai.github.io/langgraph/concepts/streaming/)
- [FastAPI BackgroundTasks — note the "after response" semantics](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [aiokafka producer idempotence](https://aiokafka.readthedocs.io/en/stable/producer.html)
- [Redis Streams `XADD` / consumer groups](https://redis.io/docs/latest/commands/xadd/)
- Cross-reference in this pack: `langchain-langgraph-streaming` (UI streaming), `langchain-debug-bundle` (callback-propagation debugging)
- Pack pain catalog: `docs/pain-catalog.md` (entries P28, P46, P47, P48, P60)
