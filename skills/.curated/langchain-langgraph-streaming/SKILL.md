---
name: langchain-langgraph-streaming
description: 'Pick the correct LangGraph 1.0 stream_mode ("messages" vs "updates"
  vs "values"),

  wire it into SSE or WebSocket without proxy-buffering gotchas, and filter

  astream_events(v2) server-side before forwarding to the browser. Use when

  building a live-token chat UI, a per-node progress bar, a debug/time-travel

  view, or diagnosing a LangGraph stream that hangs over a production proxy.

  Trigger with "langgraph streaming", "stream_mode messages", "stream_mode updates",

  "stream_mode values", "langgraph SSE", "langgraph astream_events", "SSE hangs

  behind nginx", "cloud run streaming".

  '
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
- streaming
- sse
- websocket
compatibility: Designed for Claude Code
---
# LangGraph Streaming (Python)

## Overview

An engineer ships `stream_mode="values"` to a token-level chat UI because it
"seemed the most complete." Every single token causes the full graph state —
message history, scratchpad, plan — to be re-sent and re-rendered. At ~60
tokens/sec the browser overdraws, the React reconciler can't keep up, the tab
freezes, and users blame the model. The correct answer was `stream_mode="messages"`,
which emits an `AIMessageChunk` delta per token (typically 5-50 bytes) — one
token's worth of DOM work. This is pain-catalog entry **P19** and it is the #1
LangGraph integration mistake in the 1.0 generation.

Then the same UI ships to Cloud Run and hangs forever. No error. No logs. The
server is emitting tokens; they just never reach the browser. Default proxy
buffering (Nginx, Cloud Run's HTTP/1.1 path, Cloudflare Free) holds the last
chunk waiting for more bytes. This is **P46** — SSE streams from LangGraph
drop the final `end` event over proxies that buffer — and the fix is three
headers: `X-Accel-Buffering: no`, `Cache-Control: no-cache`, `Connection: keep-alive`.

And then the debug view starts crashing browser tabs on long runs. The engineer
forwarded `astream_events(version="v2")` raw to the client because "it has more
detail" — but v2 emits thousands of events per invocation (per-token, per-node,
per-runnable lifecycle), and a 60-second agent run easily hits 3,000 events.
Browsers freeze on the JSON deserialize queue. This is **P47** — filter
server-side, forward only `on_chat_model_stream` tokens (and optionally
`on_tool_start` / `on_tool_end`).

This skill ships the decision matrix, a production-grade FastAPI SSE endpoint
with the anti-buffering headers and a 15-second heartbeat, a server-side v2
event filter that drops ~90% of noise, and a WebSocket variant with
reconnect-by-`thread_id` that resumes from the LangGraph checkpointer. Pin:
`langgraph 1.0.x`, `langchain-core 1.0.x`. Pain-catalog anchors: **P19, P46,
P47, P48, P67**, plus P16 for the `thread_id` rule and P22 for checkpointer
persistence.

## Prerequisites

- Python 3.10+
- `langgraph >= 1.0, < 2.0`, `langchain-core >= 1.0, < 2.0`
- `fastapi >= 0.110`, `uvicorn[standard]` (for SSE/WebSocket hosting)
- A checkpointer: `langgraph.checkpoint.memory.MemorySaver` for dev, or
  `langgraph.checkpoint.postgres.PostgresSaver` for prod
- Access to deploy behind your actual proxy (Nginx / Cloud Run / Cloudflare) —
  localhost does not reproduce the buffering class of bugs

## Instructions

### Step 1 — Pick the right `stream_mode` for your UI

The three modes emit fundamentally different payloads. Match the mode to the
UI shape **before** writing any server code.

| UI type | `stream_mode` | Payload each tick | Emit rate | Overdraw risk | Typical bandwidth per 5s run |
|---|---|---|---|---|---|
| Live-token chat | `"messages"` | `(AIMessageChunk, metadata)` delta | ~30-80 tokens/sec | Low | ~5-15 KB |
| Per-node progress bar / status line | `"updates"` | `{node_name: state_diff}` | 1 per node (~2-20 per run) | Low | ~1-5 KB |
| Debug / time-travel / state replay | `"values"` | Entire graph state dict | 1 per node (~2-20 per run) | **High** (state size × steps) | ~20 KB to MBs |
| Hybrid (progress + tokens) | `["updates", "messages"]` | `(mode, payload)` interleaved | Sum of above | Depends on inner modes | Sum |
| Non-browser observability | `astream_events(v2)` + filter | Filtered dicts | Depends on filter | Low (server-controlled) | Controlled |

Decision tree:

```
Do you need LLM tokens rendered live in the UI?
├── Yes → stream_mode="messages"
│         (add "updates" to the list if you also want per-node progress)
└── No, I need per-step progress
    ├── Full state for debug/replay? → stream_mode="values"
    └── Just what changed (most UIs)  → stream_mode="updates"
```

Full payload samples and combined-mode examples are in
[Stream Mode Comparison](references/stream-mode-comparison.md).

### Step 2 — Wire a minimal SSE endpoint

```python
import asyncio, json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from app.graph import build_graph

app = FastAPI()
graph = build_graph(checkpointer=MemorySaver())


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


async def stream_tokens(thread_id: str, user_input: str):
    config = {"configurable": {"thread_id": thread_id}}
    async for chunk, metadata in graph.astream(
        {"messages": [HumanMessage(user_input)]},
        config=config,
        stream_mode="messages",
    ):
        # chunk.content may be list[dict] on Claude tool-use turns (P02)
        text = chunk.text if hasattr(chunk, "text") else (
            chunk.content if isinstance(chunk.content, str) else None
        )
        if text:
            yield sse("token", {"text": text, "node": metadata.get("langgraph_node")})
    yield sse("done", {"thread_id": thread_id})
```

Always use `graph.astream(...)` (async). Never call `graph.stream(...)` (sync)
from inside an async handler — it blocks the event loop and one slow request
blocks every other connection (P48).

### Step 3 — Set the anti-buffering headers

```python
@app.get("/stream")
async def stream(thread_id: str, q: str):
    return StreamingResponse(
        stream_tokens(thread_id, q),
        media_type="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",    # Nginx / Cloud Run / Cloudflare
            "Cache-Control": "no-cache",  # Block intermediate caches
            "Connection": "keep-alive",   # Hold the TCP connection
        },
    )
```

These three headers are non-negotiable in production. Without them, your
stream works on localhost and hangs on Cloud Run. See [SSE Endpoint Template](references/sse-endpoint-template.md)
for the full template with a 15-second heartbeat (required to survive Cloud
Run's 60s idle timeout and corporate-proxy timeouts) plus reverse-proxy
snippets for Nginx, Traefik, and Cloud Run.

### Step 4 — Filter `astream_events(version="v2")` server-side

If your UI needs richer events than `"messages"` provides — tool start/end,
progress markers, retrieval events — do **not** forward `astream_events`
raw. A single 60-second agent run can emit 3,000+ events. Filter on the
server and forward only what the browser uses.

```python
FORWARD = {"on_chat_model_stream", "on_tool_start", "on_tool_end"}

async def filtered(graph, inputs, config):
    async for event in graph.astream_events(inputs, config=config, version="v2"):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            text = chunk.text if hasattr(chunk, "text") else None
            if text:
                yield {"type": "token", "text": text,
                       "node": event["metadata"].get("langgraph_node")}
        elif kind == "on_tool_start":
            yield {"type": "tool_start", "tool": event["name"]}
        elif kind == "on_tool_end":
            yield {"type": "tool_end", "tool": event["name"]}
        # Drop: on_chain_*, on_parser_*, on_prompt_*, on_retriever_* (P47)
```

Never use `astream_log()` in new code — soft-deprecated in 1.0 (P67), scheduled
for removal in 2.0. Use `astream_events(version="v2")` instead. Full event
taxonomy and compression/backpressure patterns in
[Astream Events Filtering](references/astream-events-filtering.md).

### Step 5 — WebSocket variant with reconnect

Use WebSocket instead of SSE when the user may cancel, interrupt, or send
follow-up messages mid-stream. WebSocket also sidesteps Cloudflare Free's
default response buffering.

```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/{thread_id}")
async def ws(websocket: WebSocket, thread_id: str):
    await websocket.accept()
    config = {"configurable": {"thread_id": thread_id}}  # P16 — always
    try:
        while True:
            msg = json.loads(await websocket.receive_text())
            if msg["type"] == "user_message":
                async for chunk, metadata in graph.astream(
                    {"messages": [HumanMessage(msg["text"])]},
                    config=config,
                    stream_mode="messages",
                ):
                    text = chunk.text if hasattr(chunk, "text") else None
                    if text:
                        await websocket.send_json({"type": "token", "text": text})
                await websocket.send_json({"type": "done"})
    except WebSocketDisconnect:
        pass  # Checkpointer persists state; reconnect with same thread_id resumes
```

Because LangGraph checkpointers persist state per `thread_id`, a client that
reconnects to `/ws/{same-thread-id}` automatically sees the prior conversation
history on the next turn — no special "resume" handshake required for
between-turn reconnects. For mid-stream reconnects and cancellation handling,
see [WebSocket & Reconnect](references/websocket-and-reconnect.md).

### Step 6 — Run the proxy-readiness checklist before shipping

A stream that works on `uvicorn --reload main:app` on your laptop will hang
behind Cloud Run. Before you ship, walk this checklist:

- [ ] Deployed endpoint returns `Content-Type: text/event-stream` (or `101 Switching Protocols` for WebSocket)
- [ ] Deployed endpoint returns `X-Accel-Buffering: no` and `Cache-Control: no-cache`
- [ ] `curl -N https://your.app/stream?...` shows tokens arriving incrementally — NOT all at once at the end
- [ ] Cloud Run deployed with `--use-http2` (HTTP/2 end-to-end flushes chunks reliably)
- [ ] If behind Cloudflare: Free plan may buffer — test on Pro or use a paid page rule to disable response buffering (or switch to WebSocket)
- [ ] 15-second heartbeat configured (`: heartbeat\n\n` SSE comment every 15s) so idle streams don't get killed by the 60s timeout
- [ ] Long-idle load test: run a tool-using agent that waits 45s on an API call; stream should stay alive

Test behind your actual proxy, not just localhost.

## Output

- `stream_mode` chosen deliberately from the decision matrix (`"messages"` for tokens, `"updates"` for progress, `"values"` for debug)
- Minimal FastAPI SSE endpoint using `graph.astream(..., stream_mode="messages")` in an async handler
- Required anti-buffering headers (`X-Accel-Buffering`, `Cache-Control`, `Connection`) on the `StreamingResponse`
- Server-side `astream_events(version="v2")` filter that forwards only `on_chat_model_stream` + `on_tool_start` + `on_tool_end`
- Optional WebSocket variant with `thread_id` required at the route and checkpointer-backed resume
- Proxy-readiness checklist walked end-to-end before shipping past localhost

## Error Handling

| Symptom | Cause | Fix |
|---------|-------|-----|
| Browser tab freezes on token stream | Shipped `stream_mode="values"` to a token UI; full state on every tick (P19) | Switch to `stream_mode="messages"` — emits per-token deltas only |
| Per-node progress bar never advances | Shipped `stream_mode="messages"` to a per-node UI; no node-boundary events (P19) | Switch to `stream_mode="updates"` |
| Stream works on localhost, hangs on Cloud Run | Proxy buffering holds last chunk (P46) | Add `X-Accel-Buffering: no`, `Cache-Control: no-cache` headers; deploy Cloud Run with `--use-http2` |
| Stream closes after ~60s with no data | Idle-connection timeout on proxy | Send `: heartbeat\n\n` SSE comment every 15s |
| Browser tab freezes on long `astream_events` run | Forwarded unfiltered v2 events; 3,000+ events per run (P47) | Filter server-side: forward only `on_chat_model_stream` + optional tool events |
| `DeprecationWarning: astream_log is deprecated` | Using soft-deprecated API (P67) | Migrate to `astream_events(version="v2")` |
| Agent has amnesia on every WebSocket message | Missing `thread_id` in config (P16) | Require `thread_id` at route; assert in middleware |
| `AttributeError: 'list' object has no attribute 'lower'` on chunk.content | Claude streams content blocks, not plain strings on tool-use turns (P02) | Use `chunk.text` (1.0+) or check `isinstance(chunk.content, str)` before calling string methods |
| One slow request blocks all other WebSocket clients | Sync `graph.stream()` or `graph.invoke()` inside async handler (P48) | Always use `graph.astream()` / `graph.ainvoke()` in async contexts |
| Cloudflare Free plan buffers SSE | Free-tier response buffering | Upgrade plan with page rule to disable buffering, or switch endpoint to WebSocket |

## Examples

### Live-token chat UI (the default case)

`stream_mode="messages"` plus SSE plus the three anti-buffering headers. One
token per SSE frame (~5-50 bytes each), 30-80 frames/sec during active model
generation, heartbeat every 15s during tool waits. See
[SSE Endpoint Template](references/sse-endpoint-template.md) for the complete
FastAPI example including heartbeat, reverse-proxy config, and the client
`EventSource` code.

### Per-node progress bar for a multi-step agent

`stream_mode="updates"` yields one event per node (typically 2-20 per
invocation). Render as discrete status ticks: "Planning..." → "Searching..." →
"Summarizing..." → "Done." Payload is tiny (~100 bytes per tick). Combine with
`"messages"` (`stream_mode=["updates", "messages"]`) to show both progress
ticks and streaming tokens in the active node's pane. Full payload samples in
[Stream Mode Comparison](references/stream-mode-comparison.md).

### Debug / time-travel view with `"values"`

`stream_mode="values"` yields the entire graph state after each node. Useful
for state replay, test recording, observability pipelines — **not** for
browser UIs where state size × steps × re-render quickly freezes the tab.
Pipe to a server-side log (or LangSmith), not to the browser. Example and
caveats in [Stream Mode Comparison](references/stream-mode-comparison.md).

### WebSocket with reconnect-by-`thread_id`

When users can cancel mid-stream or send follow-up messages before the
previous turn finishes. The `thread_id` is required at the route; the
checkpointer persists history; reconnecting with the same `thread_id`
automatically sees prior turns. Cancellation is implemented via
`asyncio.Task.cancel()` on the active `astream` iteration. Worked example
with half-open connection detection in
[WebSocket & Reconnect](references/websocket-and-reconnect.md).

## Resources

- [LangGraph streaming how-to](https://langchain-ai.github.io/langgraph/how-tos/streaming/)
- [LangGraph streaming concepts](https://langchain-ai.github.io/langgraph/concepts/streaming/)
- [LangChain `astream_events` v2](https://python.langchain.com/docs/how_to/streaming/#using-stream-events)
- [FastAPI `StreamingResponse`](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [Cloud Run HTTP/2 end-to-end](https://cloud.google.com/run/docs/configuring/http2)
- [Nginx `proxy_buffering` directive](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_buffering)
- Pack pain catalog: `docs/pain-catalog.md` (entries P16, P19, P22, P46, P47, P48, P67)
